# transcribe.py
import sys
import whisper

try:
    if len(sys.argv) != 2:
        print("Error: Usage: python transcribe.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]
    print(f"Loading Whisper model for {audio_file}...")
    model = whisper.load_model("base")
    print("Model loaded successfully")
    
    print("Starting transcription...")
    result = model.transcribe(audio_file)
    print("Transcription completed")
    
    print(result["text"])
except Exception as e:
    print(f"Error during transcription: {str(e)}")
    sys.exit(1)
