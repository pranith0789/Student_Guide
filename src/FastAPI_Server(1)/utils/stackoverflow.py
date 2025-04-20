import httpx
from typing import List, Tuple
import time
import asyncio
import json

STACK_API_KEY = "rl_hzCWsuykMD5YuX4wfbw5YagZ5"

BASE_SEARCH_URL = "https://api.stackexchange.com/2.3/search/advanced"
BASE_ANSWER_URL = "https://api.stackexchange.com/2.3/questions/{question_id}/answers"

# Rate limiting
RATE_LIMIT_DELAY = 1  # seconds between requests
last_request_time = 0

async def search_stackoverflow(prompt: str) -> Tuple[str, List[str]]:
    if not prompt.strip():
        return "Prompt cannot be empty.", []

    global last_request_time
    
    try:
        # Rate limiting
        current_time = time.time()
        if current_time - last_request_time < RATE_LIMIT_DELAY:
            await asyncio.sleep(RATE_LIMIT_DELAY - (current_time - last_request_time))
        last_request_time = time.time()

        params = {
            "order": "desc",
            "sort": "relevance",
            "q": prompt,
            "site": "stackoverflow",
            "key": STACK_API_KEY,
            "filter": "withbody"  # Add this to get question body
        }

        async with httpx.AsyncClient(timeout=10) as client:
            print(f"🔍 Searching Stack Overflow for: {prompt}")
            search_response = await client.get(BASE_SEARCH_URL, params=params)

            # Debug info
            print(f"Search Response Status: {search_response.status_code}")
            print(f"Search Response Headers: {dict(search_response.headers)}")

            # Check for rate limiting
            if search_response.status_code == 429:
                print("⚠️ Rate limit exceeded. Waiting before retry...")
                await asyncio.sleep(60)  # Wait 1 minute
                return await search_stackoverflow(prompt)  # Retry the request

            if search_response.status_code != 200:
                error_msg = f"Search API failed with status {search_response.status_code}"
                if search_response.status_code == 400:
                    error_msg += " - Bad request. Check your API key."
                elif search_response.status_code == 401:
                    error_msg += " - Unauthorized. Invalid API key."
                elif search_response.status_code == 403:
                    error_msg += " - Forbidden. Check your API key permissions."
                print(f"❌ {error_msg}")
                return error_msg, []

            if "application/json" not in search_response.headers.get("Content-Type", ""):
                return "Invalid content type from Stack Overflow", []

            search_data = search_response.json()
            print(f"Search Response Data: {json.dumps(search_data, indent=2)}")
            
            # Check for API errors in response
            if "error_id" in search_data:
                error_msg = f"Stack Overflow API error: {search_data.get('error_message', 'Unknown error')}"
                print(f"❌ {error_msg}")
                return error_msg, []

            if not search_data.get("items"):
                return "No relevant results found.", []

            top_question = search_data["items"][0]
            question_id = top_question["question_id"]
            question_url = top_question["link"]

            answer_params = {
                "order": "desc",
                "sort": "votes",
                "site": "stackoverflow",
                "key": STACK_API_KEY,
                "filter": "!nKzQUR3Egv"  # This filter includes the body field
            }

            print(f"💬 Fetching answers for question ID: {question_id}")
            answer_response = await client.get(BASE_ANSWER_URL.format(question_id=question_id), params=answer_params)

            # Debug info for answer response
            print(f"Answer Response Status: {answer_response.status_code}")
            print(f"Answer Response Headers: {dict(answer_response.headers)}")

            if answer_response.status_code == 429:
                print("⚠️ Rate limit exceeded. Waiting before retry...")
                await asyncio.sleep(60)
                return await search_stackoverflow(prompt)

            if answer_response.status_code != 200:
                error_msg = f"Answer API failed with status {answer_response.status_code}"
                print(f"❌ {error_msg}")
                return error_msg, [question_url]

            answers_data = answer_response.json()
            print(f"Answer Response Data: {json.dumps(answers_data, indent=2)}")

            if not answers_data.get("items"):
                return "No answers found for the top question.", [question_url]

            # Get the answer with the most votes
            answers = answers_data["items"]
            if not answers:
                return "No answers available.", [question_url]

            top_answer = max(answers, key=lambda x: x.get("score", 0))
            top_answer_text = top_answer.get("body", "").strip()  # Changed from body_markdown to body
            
            if not top_answer_text:
                return "Answer content not available.", [question_url]

            return top_answer_text, [question_url]

    except httpx.TimeoutException:
        print("⚠️ Request timed out")
        return "Request to Stack Overflow timed out. Please try again.", []
    except Exception as e:
        import traceback
        print("🔥 Exception:", str(e))
        traceback.print_exc()
        return f"Stack Overflow fetch error: {str(e)}", []

