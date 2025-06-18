from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import shutil
from pathlib import Path
import sys
import time
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    logger.info(f"Received transcription request for file: {audio.filename}")
    
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
        
        logger.info(f"File saved successfully. Size: {file_size} bytes")
        
        # Run the transcription script with timeout
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"  # Ensure Python output is not buffered
        
        logger.info("Starting transcription process...")
        result = subprocess.run(
            ["python", "transcribe.py", str(temp_path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=env
        )
        
        # Clean up the uploaded file
        os.remove(temp_path)
        
        if result.returncode == 0:
            transcription = result.stdout.strip()
            if not transcription:
                logger.error("Transcription returned empty result")
                raise HTTPException(status_code=500, detail="Transcription returned empty result")
            logger.info("Transcription completed successfully")
            return {"transcription": transcription}
        else:
            error_msg = result.stderr.strip()
            logger.error(f"Transcription failed with error: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {error_msg}")
            
    except subprocess.TimeoutExpired:
        logger.error("Transcription timed out after 5 minutes")
        if temp_path.exists():
            os.remove(temp_path)
        raise HTTPException(status_code=504, detail="Transcription timed out after 5 minutes")
    except HTTPException as he:
        if temp_path.exists():
            os.remove(temp_path)
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        if temp_path.exists():
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Whisper API is running"}

@app.get("/test")
async def test():
    return {"status": "ok", "message": "Test endpoint is working"}

if __name__ == "__main__":
    import uvicorn
    try:
        port = int(os.getenv("PORT", "5000"))
        logger.info(f"Starting server on port {port}")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            workers=1,
            timeout_keep_alive=300,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1) 