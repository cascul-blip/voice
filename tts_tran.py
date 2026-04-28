import requests
import sys
import os
from pathlib import Path

def save_as_audio(text: str, output_file: str = "output.wav", voice: str = "am_michael"):
    """Convert text to speech and save as audio file."""
    response = requests.post(
        "http://127.0.0.1:8880/v1/audio/speech",
        json={
            "model": "tts-1",
            "input": text,
            "voice": voice
        },
        timeout=1800  # Increased timeout for longer files
    )
    response.raise_for_status()

    with open(output_file, "wb") as f:
        f.write(response.content)
    print(f"✅ Audio successfully saved to: {output_file}")

def main():
    # Get input file from command line or ask user
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = input("Enter the path to your text file: ").strip()

    input_path = Path(input_path)

    if not input_path.exists():
        print(f"❌ Error: File '{input_path}' not found!")
        return

    # Read the entire text file
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print("❌ Error: The file is empty!")
        return

    print(f"📖 Read {len(text)} characters from {input_path.name}")

    # Generate output filename (same name as input but .wav)
    output_file = input_path.with_suffix(".wav")

    # Optional: Let user choose voice
    voice = input("Enter voice name (press Enter for am_michael): ").strip()
    if not voice:
        voice = "am_michael"

    # Convert to audio
    save_as_audio(text, str(output_file), voice)

if __name__ == "__main__":
    main()
