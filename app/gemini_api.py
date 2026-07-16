import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_test_cases(text):

    prompt = f"""
You are a QA Engineer.

Generate exactly 5 QA test cases.

For each test case provide:

1. Test Case ID
2. Title
3. Steps
4. Expected Result

Requirement:

{text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
    )
        if response.text is None:
            return "No QA test cases were generated."

        if len(response.text.strip()) == 0:
            return "Empty response returned by Gemini."

        return response.text

    except Exception as e:
        return f"Gemini Error: {str(e)}"