from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from models import ResumeData
from resume_builder import generate_resume
import os

app = FastAPI()

# ---------------- CORS FIX ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Production me apna domain daalna mat bhulna
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROUTES ----------------
@app.get("/")
def home():
    return {"message": "Resume Builder API is running perfectly"}

# ---------------- FILE DELETE ----------------
def delete_file(path: str):
    """PDF download hone ke baad server se delete karne ke liye."""
    if path and os.path.exists(path):
        try:
            os.remove(path)
            print(f"Successfully deleted: {path}")
        except Exception as e:
            print(f"Error deleting file: {e}")

# ---------------- GENERATE RESUME ----------------
@app.post("/generate-resume")
def create_resume(data: ResumeData, background_tasks: BackgroundTasks):
    # generate_resume function ab khud hi page check karke 
    # optimized file path return karega.
    file_path = generate_resume(data.model_dump())

    # Background task set karein taaki response ke baad file clean ho jaye
    background_tasks.add_task(delete_file, file_path)

    # File response bhejien
    return FileResponse(
        file_path,
        media_type="application/pdf",
        # Filename me spaces hta kar underscore daal rahe hain safety ke liye
        filename=f"{data.name.replace(' ', '_')}_resume.pdf"
    )