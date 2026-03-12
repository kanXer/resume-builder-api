from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import uuid
import os
from ai_objective import generate_objective # Aapka AI logic

env = Environment(loader=FileSystemLoader("templates"))

def calculate_dynamic_layout(data):
    """
    Characters count ke basis par font aur spacing decide karein.
    """
    text_parts = []
    text_parts.append(str(data.get("objective") or ""))
    
    # Safely collect experience and skills
    for job in data.get("experience", []):
        text_parts.append(str(job.get("role") or "") + str(job.get("company") or ""))
        text_parts.extend([str(p) for p in job.get("points", []) if p])
    
    text_parts.extend([str(s) for s in data.get("skills", []) if s])
    
    char_count = len(" ".join(text_parts))

    if char_count > 1800:
        return "10.5pt", "low"
    elif char_count > 900:
        return "11.5pt", "medium"
    else:
        return "13pt", "high"

def generate_resume(data):
    # --- 1. CLEANUP LOGIC (Heading hide karne ke liye) ---
    # Skills list se empty strings aur nulls hatao
    if data.get("skills"):
        data["skills"] = [s for s in data.get("skills") if s and str(s).strip()]
    else:
        data["skills"] = []

    # --- 2. AI OBJECTIVE LOGIC ---
    # Agar user ne objective nahi likha, toh AI se generate karwao
    if not data.get("objective") or str(data["objective"]).strip() == "":
        skills_str = ", ".join(data.get("skills", []))
        try:
            # AI function call
            data["objective"] = generate_objective(skills_str)
        except Exception as e:
            print(f"AI Generation failed: {e}")
            data["objective"] = "Aspiring professional seeking a challenging role to leverage my technical skills."

    # --- 3. DYNAMIC LAYOUT ---
    font_size, spacing = calculate_dynamic_layout(data)
    data["base_font_size"] = font_size
    data["section_spacing"] = spacing

    # --- 4. RENDERING ---
    template = env.get_template("simple.html")
    html = template.render(**data)

    if not os.path.exists("generated_resumes"):
        os.makedirs("generated_resumes")
        
    file_name = f"resume_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join("generated_resumes", file_name)
    
    HTML(string=html).write_pdf(file_path)

    return file_path
