from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def callGemini(system_prompt, content):
    try: 
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0
            )
        )
        # print(response.text)
        return response.text
    except Exception as e:
        # print("Call Gemini has error: ", e)
        return e