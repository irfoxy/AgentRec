import asyncio
from model.agent import Agent

async def main():
    agent=Agent('gpt-4o','user_agent','../memory/test_memory.jsonl')
    await agent.forward('what is the temperture of bejing today',[])

asyncio.run(main())
# import asyncio
# from model.agent import OpenAIBackend

# async def main():
#     agent = OpenAIBackend(model='gpt-4o')

#     # 定义一个天气工具
#     tools = [
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_weather",
#                 "description": "获取某个城市的实时天气",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "city": {"type": "string", "description": "城市名称"},
#                         "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "温度单位"}
#                     },
#                     "required": ["city"]  # city 必填
#                 }
#             }
#         }
#     ]

#     # 用户输入，询问天气
#     messages = [
#         {"role": "user", "content": "北京今天的天气怎么样？"}
#     ]

#     # 调用
#     response = await agent.chat(messages, tools=tools)
#     print(response)

# if __name__ == "__main__":
#     asyncio.run(main())
