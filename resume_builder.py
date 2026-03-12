from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import uuid
import os
from ai_objective import generate_objective

env = Environment(loader=FileSystemLoader("templates"))

def calculate_dynamic_layout(data):
    """
    Logic:
    - Chars > 1800: Font 10.5pt, low spacing
    - Chars > 900: Font 11pt, medium spacing
    - Chars <= 900: Font 12pt, high spacing
    """
    text_parts = []
    text_parts.append(str(data.get("objective") or ""))
    
    for job in data.get("experience", []):
        text_parts.append(str(job.get("role") or "") + str(job.get("company") or ""))
        text_parts.extend([str(p) for p in job.get("points", []) if p])
    
    text_parts.extend([str(s) for s in data.get("skills", []) if s])
    
    char_count = len(" ".join(text_parts))

    if char_count > 1800:
        return "10pt", "low"
    elif char_count > 900:
        return "12pt", "medium"
    else:
        return "13.5pt", "high"

def generate_resume(data):
    # --- 1. CLEANUP LOGIC ---
    if data.get("skills"):
        data["skills"] = [s for s in data["skills"] if s and str(s).strip()]
    else:
        data["skills"] = []

    # --- 2. AI OBJECTIVE LOGIC ---
    if not data.get("objective") or str(data["objective"]).strip() == "":
        skills_str = ", ".join(data.get("skills", []))
        try:
            data["objective"] = generate_objective(skills_str)
        except Exception as e:
            data["objective"] = "Focused professional with a strong technical background."

    # --- 3. DYNAMIC LAYOUT ---
    font_size, spacing_status = calculate_dynamic_layout(data)
    data["base_font_size"] = font_size
    data["section_spacing"] = spacing_status  # Yahan status (low/medium/high) jayega

    # --- 4. RENDERING ---
    template = env.get_template("simple.html")
    html = template.render(**data)

    if not os.path.exists("generated_resumes"):
        os.makedirs("generated_resumes")
        
    file_name = f"resume_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join("generated_resumes", file_name)
    
    HTML(string=html).write_pdf(file_path)

    return file_path


