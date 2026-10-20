import os, time
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from dotenv import dotenv_values
from bot_config import SYSTEM_PROMPT

cfg = dotenv_values(".env", encoding="utf-8-sig")
API_KEY = (cfg.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY", "")).strip()
client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.1-flash-lite"

def ask_bot(text: str) -> str:
    for wait in (5, 10, 20, 40, 60):
        try:
            r = client.models.generate_content(
                model=MODEL,
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0,
                ),
            )
            return r.text or ""
        except ServerError:
            print(f"server busy, waiting {wait}s...")
            time.sleep(wait)
    raise RuntimeError("Gemini unavailable after retries, try again later")