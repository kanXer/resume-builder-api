from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import uuid
import os
from ai_objective import generate_objective 

# Templates folder ka path set karein
env = Environment(loader=FileSystemLoader("templates"))

def calculate_dynamic_layout(data):
    """Characters count ke basis par font aur spacing decide karein."""
    text_parts = [str(data.get("objective") or "")]
    
    for job in data.get("experience", []):
        text_parts.append(str(job.get("role") or "") + str(job.get("company") or ""))
        text_parts.extend([str(p) for p in job.get("points", []) if p])
    
    text_parts.extend([str(s) for s in data.get("skills", []) if s])
    
    char_count = len(" ".join(text_parts))

    if char_count > 1800:
        return "10pt", "low"
    elif char_count > 1100:
        return "11pt", "medium"
    else:
        return "12pt", "high"

def generate_resume(data):
    # --- 1. CLEANUP & SANITIZATION ---
    list_fields = ["skills", "strengths", "certifications"]
    for field in list_fields:
        if data.get(field):
            data[field] = [item for item in data[field] if item and str(item).strip()]
        else:
            data[field] = []

    # Education cleanup
    if data.get("education"):
        data["education"] = [edu for edu in data["education"] if edu.get("college") or edu.get("degree")]

    # --- 2. ADDRESS SPLITTING LOGIC ---
    full_address = data.get("address", "")
    split_limit = 50 
    
    if len(full_address) > split_limit:
        last_space = full_address.rfind(' ', 0, split_limit)
        if last_space == -1: last_space = split_limit
        
        data["address_line1"] = full_address[:last_space].strip()
        data["address_line2"] = full_address[last_space:].strip()
    else:
        data["address_line1"] = full_address
        data["address_line2"] = None

    # --- 3. AI OBJECTIVE LOGIC ---
    if not data.get("objective") or str(data["objective"]).strip() == "":
        skills_str = ", ".join(data.get("skills", []))
        try:
            data["objective"] = generate_objective(skills_str)
        except Exception as e:
            print(f"AI Generation failed: {e}")
            data["objective"] = "Aspiring professional with strong technical expertise looking to contribute to innovative projects."

    # --- 4. DYNAMIC LAYOUT ---
    font_size, spacing = calculate_dynamic_layout(data)
    data["base_font_size"] = font_size
    data["section_spacing"] = spacing

    # --- 5. TEMPLATE IMPLEMENTATION (FIXED) ---
    # Hum id le rahe hain aur check kar rahe hain ki wo "1" hai ya "template1"
    raw_template_id = str(data.get("template", "1"))
    
    # Cleaning: Agar frontend se "template1.html" ya sirf "1" aaye, hume sirf number chahiye
    clean_id = raw_template_id.replace("template", "").replace(".html", "").strip()
    
    # Final file name generate karna (Taki templates/template1.html dhoonda ja sake)
    template_file = f"template{clean_id}.html"

    print(f"--- DEBUG LOG ---")
    print(f"Raw Template ID from Frontend: {raw_template_id}")
    print(f"Cleaned ID: {clean_id}")
    print(f"Targeting File: {template_file}")

    try:
        template = env.get_template(template_file)
    except Exception as e:
        print(f"ERROR: Template {template_file} not found. Error: {e}")
        # Agar error aaye toh template1.html as a fallback load karein
        template = env.get_template("template1.html")

    html_out = template.render(**data)

    # --- 6. PDF GENERATION ---
    output_dir = "generated_resumes"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    file_name = f"resume_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(output_dir, file_name)
    
    # WeasyPrint conversion
    HTML(string=html_out).write_pdf(file_path)
    
    return file_path
