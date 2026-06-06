from langchain_core.tools import tool
from ddgs import DDGS

@tool
def web_search(query: str) ->str:
    """Search the web for information on a given query. Returns top 5 results with titles and snippets."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        
        if not results:
            return "No results found."
        
        output=""
        for i,r in enumerate(results,1):
            output += f"[{i}] {r['title']}\n{r['href']}\n{r['body']}\n\n"
            return output
    
    except Exception as e:
        return f"Search failed: {str(e)}"