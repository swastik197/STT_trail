# transcribe.py
import sys
import whisper
import time

try:
    if len(sys.argv) != 2:
        print("Error: Usage: python transcribe.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]
    print(f"Loading Whisper model for {audio_file}...")
    # Use tiny model instead of base for faster loading
    model = whisper.load_model("tiny")
    print("Model loaded successfully")
    
    print("Starting transcription...")
    start_time = time.time()
    result = model.transcribe(audio_file)
    end_time = time.time()
    print(f"Transcription completed in {end_time - start_time:.2f} seconds")
    
    print(result["text"])
except Exception as e:
    print(f"Error during transcription: {str(e)}")
    sys.exit(1)
