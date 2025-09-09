from ddgs import DDGS

results = DDGS().text("python programming", max_results=5)
print(results)



# import asyncio
# import json
# from typing import Dict, List, Callable, Any, Mapping
# from dotenv import load_dotenv

# # 加载环境变量
# load_dotenv(dotenv_path='./.env')

# # 导入 Agent 类
# from model.agent import Agent

# # 定义搜索工具函数
# def search_web(query: str) -> str:
#     """搜索网络信息"""
#     # 这里只是一个模拟实现，实际应用中应该调用真实的搜索API
#     # 例如: Google Search API, SerpAPI, DuckDuckGo API等
    
#     # 模拟不同查询的搜索结果
#     search_results = {
#         "movie recommendations": [
#             "The Shawshank Redemption (1994) - IMDb rating: 9.3",
#             "The Godfather (1972) - IMDb rating: 9.2",
#             "The Dark Knight (2008) - IMDb rating: 9.0",
#             "Pulp Fiction (1994) - IMDb rating: 8.9",
#             "Forrest Gump (1994) - IMDb rating: 8.8"
#         ],
#         "best movies 2023": [
#             "Oppenheimer (2023) - IMDb rating: 8.6",
#             "Spider-Man: Across the Spider-Verse (2023) - IMDb rating: 8.7",
#             "Barbie (2023) - IMDb rating: 7.1",
#             "Killers of the Flower Moon (2023) - IMDb rating: 8.0",
#             "Poor Things (2023) - IMDb rating: 8.3"
#         ],
#         "action movies": [
#             "John Wick: Chapter 4 (2023) - IMDb rating: 7.8",
#             "Mission: Impossible - Dead Reckoning Part One (2023) - IMDb rating: 7.8",
#             "Extraction 2 (2023) - IMDb rating: 7.0",
#             "The Batman (2022) - IMDb rating: 7.9",
#             "Top Gun: Maverick (2022) - IMDb rating: 8.3"
#         ]
#     }
    
#     # 查找最匹配的查询
#     best_match = None
#     for key in search_results:
#         if key in query.lower():
#             best_match = key
#             break
    
#     if best_match:
#         result = f"Search results for '{query}':\n" + "\n".join(f"- {movie}" for movie in search_results[best_match])
#     else:
#         result = f"Search results for '{query}':\n- No specific results found. Try more specific queries like 'movie recommendations', 'best movies 2023', or 'action movies'."
    
#     return result

# # 定义工具模式 (搜索工具)
# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "search_web",
#             "description": "Search the web for information about movies, news, or other topics",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "query": {
#                         "type": "string",
#                         "description": "The search query to look up information"
#                     }
#                 },
#                 "required": ["query"]
#             }
#         }
#     }
# ]

# # 创建工具注册表 (搜索工具)
# tool_registry = {
#     "search_web": search_web
# }

# async def test_agent():
#     # 创建 Agent 实例
#     # 使用一个不存在的内存文件路径，这样就不会尝试读取内存
#     agent = Agent(
#         planner_model="gpt-4o",  # 或者您使用的模型
#         exec_model="gpt-4o",
#         memory_model="gpt-4o",
#         role="assistant",
#         memory_path="../memory/test_memory.jsonl"  # 不存在的文件路径
#     )
    
#     # 测试搜索问题
#     test_questions = [
#         """
# Here are some movies I'm considering:

# Inception

# Titanic

# Interstellar

# Zootopia

# The Godfather

# Avatar

# Avengers: Endgame

# Green Book

# The Legend of 1900

# Spirited Away

# I generally enjoy watching interesting movies that aren't too slow or boring. I have some interest in sci-fi and animated films, but I'm open to other genres too. Just looking for something entertaining and well-made.


# Could you recommend one movies from the list above that you think I might enjoy
#     """,
#     ]
    
#     for i, question in enumerate(test_questions):
#         print(f"\n{'='*50}")
#         print(f"Test {i+1}: {question}")
#         print(f"{'='*50}")
        
#         try:
#             result = await agent.forward(
#                 question=question,
#                 tools=[],  # 传入搜索工具
#                 tool_registry=tool_registry  # 传入工具注册表
#             )
#             print(f"\nFinal Result: {result}")
#             await agent.backward(user_id=346,feedback='Great!,I Like it')
#         except Exception as e:
#             print(f"Error during test {i+1}: {e}")
#             # 打印更详细的错误信息
#             import traceback
#             traceback.print_exc()

# if __name__ == "__main__":
#     # 运行测试
#     asyncio.run(test_agent())