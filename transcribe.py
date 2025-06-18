# transcribe.py
import sys
import whisper
import os
import torch
import time

def main():
    try:
        if len(sys.argv) != 2:
            print("Error: Usage: python transcribe.py <audio_file>")
            sys.exit(1)

        audio_file = sys.argv[1]
        if not os.path.exists(audio_file):
            print(f"Error: Audio file not found: {audio_file}")
            sys.exit(1)

        # Load model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = whisper.load_model("tiny", device=device)
        
        # Load and transcribe the audio
        audio = whisper.load_audio(audio_file)
        result = model.transcribe(audio)
        
        if "text" in result:
            # Only print the transcription text
            print(result["text"].strip())
        else:
            print("Error: No transcription text in result")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
