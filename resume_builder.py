from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from weasyprint import HTML
import uuid
import os
import pypdf
from ai_objective import generate_objective 

# Templates folder setup
env = Environment(loader=FileSystemLoader("templates"))

def get_page_count(file_path):
    """PDF ke total pages count karta hai."""
    try:
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            return len(reader.pages)
    except Exception as e:
        print(f"Error checking page count: {e}")
        return 1

def generate_resume(data):
    # --- 1. DATA CLEANUP & SANITIZATION ---
    for field in ["skills", "strengths"]:
        data[field] = [item for item in data.get(field, []) if item and str(item).strip()]
    
    if data.get("certifications"):
        data["certifications"] = [c for c in data["certifications"] if c.get("title") and str(c.get("title")).strip()]
    else:
        data["certifications"] = []

    if data.get("education"):
        data["education"] = [edu for edu in data["education"] if edu.get("college") or edu.get("degree")]

    # --- 2. TEMPLATE SELECTION (Frontend Se Aane Wala Name) ---
    # Default template agar kuch na mile
    DEFAULT_TEMPLATE = "template1.html"
    
    # Frontend se template name nikalna
    requested_template = data.get("template", DEFAULT_TEMPLATE).strip()

    # Extension check aur fix
    if not requested_template.lower().endswith(".html"):
        requested_template += ".html"

    try:
        template = env.get_template(requested_template)
        print(f"Loading Template: {requested_template}")
    except TemplateNotFound:
        print(f"Warning: {requested_template} nahi mila. Using {DEFAULT_TEMPLATE}")
        template = env.get_template(DEFAULT_TEMPLATE)
    except Exception as e:
        print(f"Template error: {e}")
        template = env.get_template(DEFAULT_TEMPLATE)

    # --- 3. ADDRESS SPLITTING LOGIC ---
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

    # --- 4. AI OBJECTIVE LOGIC ---
    if not data.get("objective") or str(data["objective"]).strip() == "":
        skills_str = ", ".join(data.get("skills", []))
        try:
            data["objective"] = generate_objective(skills_str)
        except Exception as e:
            print(f"AI Generation failed: {e}")
            data["objective"] = "Aspiring professional with strong technical expertise looking to contribute to innovative projects."

    # --- 5. AUTO-FIT LOOP ---
    configs = [
        {"font": "16pt", "spacing": "vhigh"},
        {"font": "15pt", "spacing": "vhigh"},
        {"font": "14pt", "spacing": "high"},
        {"font": "13pt", "spacing": "high"},
        {"font": "12pt", "spacing": "medium"},
        {"font": "11pt", "spacing": "medium"},
        {"font": "10.5pt", "spacing": "low"},
        {"font": "10pt", "spacing": "low"}
    ]

    output_dir = "generated_resumes"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    last_generated_path = ""

    for config in configs:
        data["base_font_size"] = config["font"]
        data["section_spacing"] = config["spacing"]

        html_out = template.render(**data)
        
        file_name = f"resume_{uuid.uuid4().hex}.pdf"
        current_path = os.path.join(output_dir, file_name)
        
        HTML(string=html_out).write_pdf(current_path)

        # Optimization: Pichli file delete karo agar wo fit nahi hui thi
        if last_generated_path and os.path.exists(last_generated_path):
            try:
                os.remove(last_generated_path)
            except:
                pass
        
        last_generated_path = current_path
        
        # Check if it fits on 1 page
        if get_page_count(current_path) == 1:
            print(f"Success: Resume fit on 1 page with {config['font']} font.")
            return current_path

    print("Warning: Content too long. Returning 10pt version (multiple pages).")
    return last_generated_path