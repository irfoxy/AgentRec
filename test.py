import asyncio
import json
from typing import Dict, List, Callable, Any, Mapping
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path='./.env')

# 导入 Agent 类
from model.agent import Agent

# 定义计算工具函数
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        # 安全地计算表达式
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters"
        
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"

# 定义工具模式 (只保留计算工具)
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# 创建工具注册表 (只保留计算工具)
tool_registry = {
    "calculate": calculate
}

async def test_agent():
    # 创建 Agent 实例
    # 使用一个不存在的内存文件路径，这样就不会尝试读取内存
    agent = Agent(
        model="gpt-3.5-turbo",  # 或者您使用的模型
        role="assistant",
        memory_path="../memory/test_memory.jsonl"  # 不存在的文件路径
    )
    
    # 测试计算问题
    test_questions = [
        "Calculate the result of 15 * 8 + 20 / 4",
    ]
    
    for i, question in enumerate(test_questions):
        print(f"\n{'='*50}")
        print(f"Test {i+1}: {question}")
        print(f"{'='*50}")
        
        try:
            result = await agent.forward(
                question=question,
                tools=tools,
                tool_registry=tool_registry
            )
            print(f"\nFinal Result: {result}")
        except Exception as e:
            print(f"Error during test {i+1}: {e}")
            # 打印更详细的错误信息
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_agent())