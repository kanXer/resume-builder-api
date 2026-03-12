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
    allow_origins=["*"],   # dev ke liye (production me domain daalna)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROUTES ----------------

@app.get("/")
def home():
    return {"message": "Resume Builder API running"}

# ---------------- FILE DELETE ----------------

def delete_file(path: str):
    if os.path.exists(path):
        os.remove(path)

# ---------------- GENERATE RESUME ----------------

@app.post("/generate-resume")
def create_resume(data: ResumeData, background_tasks: BackgroundTasks):

    file_path = generate_resume(data.model_dump())

    background_tasks.add_task(delete_file, file_path)

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="resume.pdf"
    )
