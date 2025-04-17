import httpx
from typing import List, Tuple

STACK_API_KEY = "rl_hzCWsuykMD5YuX4wfbw5YagZ5"

BASE_SEARCH_URL = "https://api.stackexchange.com/2.3/search/advanced"
BASE_ANSWER_URL = "https://api.stackexchange.com/2.3/questions/{question_id}/answers"

async def search_stackoverflow(prompt: str) -> Tuple[str, List[str]]:
    try:
        params = {
            "order": "desc",
            "sort": "relevance",
            "q": prompt,
            "site": "stackoverflow",
            "key": STACK_API_KEY
        }

        async with httpx.AsyncClient(timeout=10) as client:
            print(f"🔍 Searching Stack Overflow for: {prompt}")
            search_response = await client.get(BASE_SEARCH_URL, params=params)

            if search_response.status_code != 200:
                error_msg = f"Search API failed with status {search_response.status_code}: {search_response.text}"
                print(error_msg)
                return error_msg, []

            search_data = search_response.json()
            if not search_data.get("items"):
                print("❌ No Stack Overflow questions found.")
                return "No relevant Stack Overflow results found.", []

            top_question = search_data["items"][0]
            question_id = top_question["question_id"]
            question_url = top_question["link"]

            # Fetch top answer
            answer_params = {
                "order": "desc",
                "sort": "votes",
                "site": "stackoverflow",
                "key": STACK_API_KEY,
                "filter": "!)rTkraWjJY0cV9W_2DwE"
            }

            print(f"💬 Fetching answers for question ID: {question_id}")
            answer_response = await client.get(BASE_ANSWER_URL.format(question_id=question_id), params=answer_params)

            if answer_response.status_code != 200:
                error_msg = f"Answer API failed with status {answer_response.status_code}: {answer_response.text}"
                print(error_msg)
                return error_msg, [question_url]

            answers_data = answer_response.json().get("items", [])
            if not answers_data:
                print("❌ No answers found for the top question.")
                return "No answers found for the top Stack Overflow question.", [question_url]

            top_answer_text = answers_data[0].get("body_markdown", "").strip()
            return top_answer_text, [question_url]

    except Exception as e:
        print("🔥 Exception:", str(e))
        return f"Stack Overflow fetch error: {str(e)}", []
