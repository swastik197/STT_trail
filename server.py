from fastapi import FastAPI, UploadFile, File, HTTPException
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
        # Check file size
        file_size = 0
        with open(temp_path, "wb") as buffer:
            while chunk := await audio.read(8192):
                file_size += len(chunk)
                if file_size > 100 * 1024 * 1024:  # 100MB limit
                    raise HTTPException(status_code=400, detail="File too large. Maximum size is 100MB")
                buffer.write(chunk)
        
        print(f"Saved file to: {temp_path} (size: {file_size/1024/1024:.2f}MB)")
        
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
            transcription = result.stdout.strip()
            if not transcription:
                raise HTTPException(status_code=500, detail="Transcription returned empty result")
            return {"transcription": transcription}
        else:
            error_msg = result.stderr.strip()
            print(f"Transcription failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {error_msg}")
            
    except subprocess.TimeoutExpired:
        print("Transcription timed out after 5 minutes")
        if temp_path.exists():
            os.remove(temp_path)
        raise HTTPException(status_code=504, detail="Transcription timed out after 5 minutes")
    except HTTPException as he:
        if temp_path.exists():
            os.remove(temp_path)
        raise he
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        # Clean up in case of error
        if temp_path.exists():
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

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