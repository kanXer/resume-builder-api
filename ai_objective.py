import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Generation config: Isse response aur bhi predictable ho jayega
generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 1000,
}

# Model name ko update karein (Current stable version use karein)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", # Change this to a valid version
    generation_config=generation_config
)

def generate_objective(skills):
    skill_text = ", ".join(skills) if skills else "general technical skills"

    # Prompt ko thoda "instruction-heavy" banaya hai


    prompt = f"""
    Write a professional resume objective for a candidate with: {skill_text}.

    Requirements:
    - Length: Exactly 2 to 3 sentences (approx 40 words).
    - Content: Mention how these skills solve business problems.
    - Format: Plain text only and must add full stop at the end, no formatting.
    """
    try:
        response = model.generate_content(prompt)

        if response and response.text:
            return response.text.strip().replace('"', '') # Quotes bhi remove kar dega
        return "Motivated and detail-oriented individual seeking an entry-level opportunity where I can use my skills, learn new things, and contribute positively to the growth of the organization."

    except Exception as e:
        print("Gemini error:", e)
        return "Motivated and detail-oriented individual seeking an entry-level opportunity where I can use my skills, learn new things, and contribute positively to the growth of the organization."