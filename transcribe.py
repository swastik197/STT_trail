# transcribe.py
import sys
import whisper
import os
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) != 2:
        logger.error("Usage: python transcribe.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]
    if not os.path.exists(audio_file):
        logger.error(f"Audio file not found: {audio_file}")
        sys.exit(1)

    try:
        # Log system information
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Audio file size: {os.path.getsize(audio_file)} bytes")
        
        logger.info("Loading Whisper model...")
        model = whisper.load_model("base")
        logger.info("Model loaded successfully")

        logger.info(f"Transcribing audio file: {audio_file}")
        result = model.transcribe(audio_file)
        
        if not result:
            logger.error("Transcription failed - result is None")
            sys.exit(1)
            
        if "text" not in result:
            logger.error(f"Transcription failed - unexpected result format: {result}")
            sys.exit(1)
            
        transcription = result["text"].strip()
        if not transcription:
            logger.error("Transcription returned empty text")
            sys.exit(1)
            
        logger.info("Transcription completed successfully")
        print(transcription)
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
