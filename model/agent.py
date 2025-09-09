from __future__ import annotations
import os
from typing import Any, Dict, List
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
import logging
import colorlog
from dotenv import load_dotenv
import json
from typing import Callable, Mapping, Tuple

MAX_CYC=5
MEMORY_RECENT_K=10

# 配置注释
LOG_FORMAT = '%(log_color)s%(levelname)-8s%(reset)s %(message)s'
colorlog.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path='./.env')

# 抽象类
class ChatBackend:
    async def chat(self, *_, **__) -> Dict[str, Any]:
        raise NotImplementedError

# Backend类
class OpenAIBackend(ChatBackend):
    def __init__(self, model: str):
        self.model = model
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )

    # retry 修饰器，调用此函数失败时自动重试
    @retry(
        # 最大尝试次数
        stop=stop_after_attempt(3),
        # 指数退避等待时间
        wait=wait_exponential(multiplier=1, min=2, max=10),
        # 抛出原本异常
        reraise=True,
        # 重试前打印日志
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] | None = None,
        tool_choice: str | None = "auto",
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        # 获取当前尝试次数
        current_attempt = getattr(self.chat.retry.statistics, "attempt_number", 0)
        # 装填消息
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice

        # 请求
        try:
            resp = await self.client.chat.completions.create(**payload)
        except Exception as e:
            logger.error(
                f"OpenAI API call attempt {current_attempt} failed with error: {type(e).__name__} - {e}"
            )
            raise

        msg = resp.choices[0].message
        raw_calls = getattr(msg, "tool_calls", None)
        # 处理function call
        tool_calls = None
        if raw_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in raw_calls
            ]
        return {"content": msg.content, "tool_calls": tool_calls}

# 规划Prompt
META_SYSTEM_PROMPT = (
    "You are the META-PLANNER in a hierarchical AI system. A user will ask a\n"
    "high-level question. **First**: break the problem into a *minimal sequence*\n"
    "of executable tasks. Reply ONLY in JSON with the schema:\n"
    "{ \"plan\": [ {\"id\": INT, \"description\": STRING} … ] }\n\n"
    "After each task is executed by the EXECUTOR you will receive its result.\n"
    "Please carefully consider the descriptions of the time of web pages and events in the task, and take these factors into account when planning and giving the final answer.\n"
    "If the final answer is complete, output it with the template:\n"
    "FINAL ANSWER: <answer>\n\n"
    " YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.\n"
    "Please ensure that the final answer strictly follows the question requirements, without any additional analysis.\n"
    "If the final ansert is not complete, emit a *new* JSON plan for the remaining work. Keep cycles as\n"
    "few as possible. Never call tools yourself — that's the EXECUTOR's job."
    "⚠️ Reply with *pure JSON only*."
)

EXEC_SYSTEM_PROMPT = (
    "You are the EXECUTOR sub-agent. You will first receive an initial task description from the user, and then you will receive one subtask at a time from the meta-planner."
    "Your job is to complete the subtask, using available tools via function calling if needed."
    "If no tools are available or tool calling is unnecessary, analyze the question and historical records to provide a natural language response."
    "If you must call a tool, generate the appropriate function call instead of natural language."
    "When done, do NOT output FINAL ANSWER."
)

MEMORY_UPDATER_PROMPT="""
You are a memory-updater sub-agent. You receive a dialogue between the user and the assistant, 
reference the feedback provided by the user at the end, extract all useful information from the entire conversation, and return it separated by carriage returns.
Each line should be as concise and brief as possible.
"""

class Agent:
    def __init__(self,planner_model:str,exec_model:str,memory_model:str,role:str,memory_path:str) -> None:
        self.planner=OpenAIBackend(model=planner_model)
        self.exec=OpenAIBackend(model=exec_model)
        self.memory_updater=OpenAIBackend(model=memory_model)

        self.role=role
        self.memory_path=memory_path

        self.planner_msgs=[]
    
    def extract_memory(self):
        with open(self.memory_path,'r',encoding='utf-8') as f:
            memory_list=[json.loads(line) for line in f if line.strip()]

        memory_list=[memory for memory in memory_list if memory.get("role")==self.role]
        memory_list=memory_list[-MEMORY_RECENT_K:]

        return memory_list

    def build_memory_prompt(self,memory_list):
        return memory_list

    def extract_plan_lst(self,raw_content:str):
        try:
            plan_lst=json.loads(raw_content)['plan']
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"EXTRACT FAILED: {e}")
        return plan_lst

    async def _run_executor_once(
        self,
        exec_msgs: List[Dict[str, Any]],
        tools_schema: List[Dict[str, Any]],
        tool_registry: Mapping[str, Callable[..., Any]] | None = None,
    ) -> str:
        current_msgs =exec_msgs.copy()
        resp = await self.exec.chat(current_msgs, tools=tools_schema, tool_choice="auto")
        while resp.get("tool_calls"):
            if not tool_registry:
                raise RuntimeError("Tool Registry not provided")

            current_msgs.append({
                "role": "assistant",
                "content": None,
                "tool_calls": resp["tool_calls"],
            })

            for tc in resp["tool_calls"]:
                name = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"] or "{}")
                if name not in tool_registry:
                    raise RuntimeError(f"UNKNOWN_TOOL: {name}")
                try:
                    result = tool_registry[name](**args)
                except TypeError:
                    result = tool_registry[name](**args)

                current_msgs.append({
                    "role": "function",
                    "tool_call_id": tc["id"],
                    "name": name,
                    "content": json.dumps(result, ensure_ascii=False),
                })
            resp = await self.exec.chat(current_msgs, tools=tools_schema, tool_choice="none")

        return resp["content"] or ""

    async def forward(self, question: str, tools: List[Dict[str, Any]], tool_registry: Mapping[str, Callable[..., Any]] | None = None):

        self.planner_msgs = [
            {"role": "system", "content": META_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        memory_list = self.extract_memory()
        if memory_list:
            memory_prompt = self.build_memory_prompt(memory_list)
            self.planner_msgs.append({"role": "user", "content": memory_prompt})

        for cyc in range(MAX_CYC):
            resp = await self.planner.chat(self.planner_msgs)
            content = resp["content"] or ""
            print({"content": content, "tool_calls": resp["tool_calls"]})

            if content.strip().upper().startswith("FINAL ANSWER:"):
                self.planner_msgs.append({"role":"assistant","content":content})
                final_ans = content.split(":", 1)[1].strip()
                print("FINAL ANSWER =>", final_ans)
                return final_ans

            plan_lst = self.extract_plan_lst(content)
            self.planner_msgs.append({'role':'assistant',"content":resp["content"]})
            
            exec_msgs=[{"role": "system", "content": EXEC_SYSTEM_PROMPT}]
            exec_msgs.append({"role":"user","content":question})

            for task in plan_lst:
                task_id = task.get("id")
                task_desc = task.get("description", "")
                print
                print(f"[EXECUTE] Task {task_id}: {task_desc}")
                exec_msgs.append({"role":"assistant","content":task_desc})

                result_text = await self._run_executor_once(
                    exec_msgs=exec_msgs,
                    tools_schema=tools,
                    tool_registry=tool_registry,
                )
                print(f"[RESULT] Task {task_id}: {result_text}")

                exec_msgs.append({
                    "role": "assistant",
                    "content": f"Result for task {task_id}: {result_text}",
                })
                self.planner_msgs.append({
                    "role": "assistant",
                    "content": f"Result for task {task_id}: {result_text}",
                })
            self.planner_msgs.append({
                    "role": "user",
                    "content": "All task results have been given above,try if you can give the FINAL answer.If can't create another plan instead",
                })
        else:
            raise RuntimeError("Reached MAX_CYC but no FINAL ANSWER was produced.")
    
    async def backward(self,user_id:int,feedback:str):
        self.planner_msgs.append({'role':'user','content':feedback})
        self.planner_msgs=self.planner_msgs[1:]
        
        history=""
        for row in self.planner_msgs:
            history+=f"\n{row['role']}:{row['content']}"
            history+='\n-------------------------------------------------'

        memory_updater_msgs=[
            {"role":"system","content":MEMORY_UPDATER_PROMPT},
            {"role":"user","content":history}
        ]

        resp=await self.memory_updater.chat(memory_updater_msgs)
        memory={"user_id":user_id,"role":self.role,memory:resp['content'].split('\n')}
        with open(self.memory_path,'a',encoding='utf-8') as f:
            f.write(json.dumps(memory,ensure_ascii=False)+'\n')
        print(f"[MEMORY] saved")
        
        