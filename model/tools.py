from ddgs import DDGS

async def search(text: str, max_results: int):
    """
    Asynchronously search DuckDuckGo for the given text query and return results.
    
    This function uses the DuckDuckGo Search API to retrieve text-based search results
    for the specified query. It returns a list of search results in the form of dictionaries
    containing titles, URLs, and descriptions.
    
    Args:
        text (str): The search query string to look up.
        max_results (int): Maximum number of search results to return.
        
    Returns:
        list: A list of dictionaries containing search results. Each dictionary contains
              keys for 'title', 'href' (URL), and 'body' (description).
              
    Note:
        This is an asynchronous function and needs to be awaited. The actual implementation
        uses a synchronous DDGS client inside an async function, which might block the event loop.
        For production use, consider running the synchronous client in a thread pool.
    """
    try:
        results = DDGS().text(text, max_results=max_results)
    except:
        print("[SEARCH FAILED]")
        return 'Search failed'
    return results