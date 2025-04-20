import os
import aiohttp
from typing import Tuple, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv("credententials.env")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

async def search_youtube(query: str) -> Tuple[str, List[str]]:
    """Search YouTube for videos."""
    if not YOUTUBE_API_KEY:
        print("YouTube API key missing")
        return "YouTube API key not provided.", []
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": 3,
                "key": YOUTUBE_API_KEY,
                "order": "relevance",
            }
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    print(f"YouTube API error: HTTP {response.status}")
                    return f"YouTube API error: HTTP {response.status}", []
                data = await response.json()
                if "error" in data:
                    print(f"YouTube API error: {data['error']['message']}")
                    return f"YouTube API error: {data['error']['message']}", []
                videos = []
                sources = []
                for item in data.get("items", []):
                    title = item["snippet"]["title"]
                    description = item["snippet"]["description"][:200] + ("..." if len(item["snippet"]["description"]) > 200 else "")
                    video_id = item["id"]["videoId"]
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    videos.append(f"Title: {title}\nDescription: {description}")
                    sources.append(video_url)
                video_text = "\n\n".join([f"YouTube Video {i+1}:\n{vid}" for i, vid in enumerate(videos)])
                return video_text or "No relevant YouTube videos found.", sources
    except Exception as e:
        print(f"YouTube API error: {str(e)}")
        return "Failed to fetch YouTube videos.", [] 