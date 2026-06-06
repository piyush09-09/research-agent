import httpx
from bs4 import BeautifulSoup
from langchain_core.tools import tool

@tool
def scrape_url(url:str) ->str:
    """Scrape a webpage and return its main text content. Use this to read full articles."""
    try:
        response = httpx.get(url, timeout =15, follow_redirects = True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip= True)

        if len(text)> 3000:
            text = text[:3000] + "\n...[truncated]"
        
        return text if text else "Could not extract text from page"

    except Exception as e:
        return f"Scrape Failed: {str(e)}"
