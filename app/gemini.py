import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

async def call_gemini(message: str, max_tokens: int = 1024) -> dict:
    api_key = os.getenv("GROQ_API_KEY")

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ],
        "max_tokens": max_tokens
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        print("API KEY EXISTS:", api_key is not None)
        print("STATUS:", response.status_code)
        print("BODY:", response.text)

        response.raise_for_status()

        data = response.json()

    text = data["choices"][0]["message"]["content"]
    tokens = data.get("usage", {}).get("total_tokens", 0)

    return {
        "response": text,
        "tokens_used": tokens
    }