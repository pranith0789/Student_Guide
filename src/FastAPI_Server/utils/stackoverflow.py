import os
import aiohttp
from typing import Tuple, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv("credententials.env")
STACKOVERFLOW_KEY = os.getenv("STACKOVERFLOW_KEY")  # Optional

async def search_stackoverflow(query: str) -> Tuple[str, List[str]]:
    """Search Stack Overflow for answers."""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                "q": query,
                "site": "stackoverflow",
                "sort": "relevance",
                "order": "desc",
                "filter": "withbody",
                "pagesize": 3,
            }
            if STACKOVERFLOW_KEY:
                params["key"] = STACKOVERFLOW_KEY
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                answers = []
                sources = []
                
                for item in data.get("items", []):
                    if item.get("is_answered") and item.get("accepted_answer_id"):
                        title = item.get("title", "")
                        body = item.get("body", "")
                        link = item.get("link", "")
                        
                        answers.append(body)
                        sources.append(link)
                
                answer_text = "\n\n".join([f"Stack Overflow Result {i+1}:\n{ans}" for i, ans in enumerate(answers)])
                return answer_text or "No relevant Stack Overflow answers found.", sources
    except Exception as e:
        print(f"Stack Overflow API error: {str(e)}")
        return "Failed to fetch Stack Overflow answers.", [] 