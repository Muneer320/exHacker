import asyncio
import os
from dotenv import load_dotenv

# Load env file
load_dotenv(".env")

groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

print("GROQ_API_KEY:", groq_key)
print("GEMINI_API_KEY:", gemini_key)

async def test_groq():
    print("\n--- Testing Groq ---")
    if not groq_key:
        print("Groq API key not set in env.")
        return
    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=groq_key)
        response = await client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model="llama3-70b-8192",
            max_tokens=10
        )
        print("Groq Success:", response.choices[0].message.content)
    except Exception as e:
        print("Groq Error:", type(e), e)

async def test_gemini():
    print("\n--- Testing Gemini ---")
    if not gemini_key:
        print("Gemini API key not set in env.")
        return
    try:
        from google import genai as google_genai
        client = google_genai.Client(api_key=gemini_key)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Hello",
        )
        print("Gemini Success:", response.text)
    except Exception as e:
        print("Gemini Error:", type(e), e)

async def main():
    await test_groq()
    await test_gemini()

if __name__ == "__main__":
    asyncio.run(main())
