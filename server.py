from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import shutil
from pathlib import Path
import sys
import time

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
print(f"Upload directory created at: {UPLOAD_DIR.absolute()}")

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    print(f"Received request to transcribe: {audio.filename}")
    start_time = time.time()
    
    # Save the uploaded file
    temp_path = UPLOAD_DIR / audio.filename
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        print(f"Saved file to: {temp_path}")
        
        # Run the transcription script with timeout
        print("Starting transcription...")
        result = subprocess.run(
            ["python", "transcribe.py", str(temp_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Clean up the uploaded file
        os.remove(temp_path)
        end_time = time.time()
        print(f"Total processing time: {end_time - start_time:.2f} seconds")
        
        if result.returncode == 0:
            return {"transcription": result.stdout.strip()}
        else:
            print(f"Transcription failed: {result.stderr}")
            return {"error": result.stderr.strip()}
            
    except subprocess.TimeoutExpired:
        print("Transcription timed out after 5 minutes")
        if temp_path.exists():
            os.remove(temp_path)
        return {"error": "Transcription timed out after 5 minutes"}
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        # Clean up in case of error
        if temp_path.exists():
            os.remove(temp_path)
        return {"error": str(e)}

@app.get("/")
async def root():
    print("Health check endpoint called")
    return {"message": "Whisper API is running"}

@app.get("/test")
async def test():
    print("Test endpoint called")
    return {"status": "ok", "message": "Test endpoint is working"}

if __name__ == "__main__":
    import uvicorn
    try:
        port = int(os.getenv("PORT", "5000"))
        print(f"Starting server on port {port}")
        print(f"Python version: {sys.version}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
        # Use a single worker and increase timeout
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            workers=1,
            timeout_keep_alive=300,
            log_level="debug"
        )
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        sys.exit(1) 