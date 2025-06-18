from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import shutil
from pathlib import Path

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    # Save the uploaded file
    temp_path = UPLOAD_DIR / audio.filename
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # Run the transcription script
        result = subprocess.run(
            ["python", "transcribe.py", str(temp_path)],
            capture_output=True,
            text=True
        )
        
        # Clean up the uploaded file
        os.remove(temp_path)
        
        if result.returncode == 0:
            return {"transcription": result.stdout.strip()}
        else:
            return {"error": result.stderr.strip()}
            
    except Exception as e:
        # Clean up in case of error
        if temp_path.exists():
            os.remove(temp_path)
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"message": "Whisper API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "5000"))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 