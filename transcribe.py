# transcribe.py
import sys
import whisper
import os
import torch

def main():
    try:
        if len(sys.argv) != 2:
            print("Error: Usage: python transcribe.py <audio_file>")
            sys.exit(1)

        audio_file = sys.argv[1]
        if not os.path.exists(audio_file):
            print(f"Error: Audio file not found: {audio_file}")
            sys.exit(1)

        print(f"Loading Whisper model for {audio_file}...")
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # Use tiny model for faster processing
        model = whisper.load_model("tiny", device=device)
        print("Model loaded successfully")
        
        print("Starting transcription...")
        result = model.transcribe(audio_file)
        print("Transcription completed")
        
        if "text" in result:
            print(result["text"])
        else:
            print("Error: No transcription text in result")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
