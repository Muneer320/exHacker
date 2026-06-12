import os
import asyncio
from dotenv import load_dotenv

load_dotenv(".env")

async def list_groq():
    print("--- Groq Models ---")
    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        models = await client.models.list()
        for m in models.data:
            print(f" - {m.id} (owned by {m.owned_by})")
    except Exception as e:
        print("Groq list error:", e)

def list_gemini():
    print("--- Gemini Models ---")
    try:
        from google import genai as google_genai
        client = google_genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        for m in client.models.list():
            print(f" - {m.name} (supported: {m.supported_actions})")
    except Exception as e:
        print("Gemini list error:", e)

async def main():
    await list_groq()
    list_gemini()

if __name__ == "__main__":
    asyncio.run(main())
