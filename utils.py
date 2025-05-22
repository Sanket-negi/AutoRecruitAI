import google.generativeai as genai
def simple_match_score(resume_text: str, job_desc: str) -> int:
    resume_words = set(resume_text.lower().split())
    job_words = set(job_desc.lower().split())
    return len(resume_words.intersection(job_words))

import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

#def generate_message_gemma(prompt: str) -> str:
    # import subprocess
    # try:
    #     process = subprocess.run(
    #         ["ollama", "run", "gemma:2b"],
    #         input=prompt,
    #         text=True,
    #         capture_output=True,
    #         timeout=30
    #     )
    #     if process.returncode != 0:
    #         stderr = process.stderr.strip() if process.stderr else "No stderr"
    #         stdout = process.stdout.strip() if process.stdout else "No stdout"
    #         return f"Error:\n{stderr}\n{stdout}"
    #     return process.stdout.strip()
    # except Exception as e:
    #     return f"Exception: {str(e)}"
      # Replace with your actual key


def generate_message_gemma(prompt: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": 150}
        )
        return response.text.strip()
    except Exception as e:
        return f"Exception: {str(e)}"
