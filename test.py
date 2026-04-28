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
    # Get input directory from command line or ask user
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    else:
        input_dir = input("Enter the path to your text files directory: ").strip()

    input_dir = Path(input_dir)

    if not input_dir.exists():
        print(f"❌ Error: Directory '{input_dir}' not found!")
        return
    if not input_dir.is_dir():
        print(f"❌ Error: '{input_dir}' is not a directory!")
        return

    # Find all .txt files in the directory
    txt_files = list(input_dir.glob("*.txt"))

    if not txt_files:
        print("⚠️ No .txt files found in the specified directory!")
        return

    print(f"📁 Found {len(txt_files)} .txt file(s) to process:")
    for i, file_path in enumerate(txt_files, 1):
        print(f"{i}. {file_path.name}")

    # Optional: Let user choose voice (same as before)
    voice = input("\nEnter voice name (press Enter for am_michael): ").strip()
    if not voice:
        voice = "am_michael"

    # Process each text file
    for i, txt_file in enumerate(txt_files, 1):
        print(f"\n📄 Processing {i}/{len(txt_files)}: {txt_file.name}")

        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                text = f.read().strip()

            if not text:
                print(f"⚠️ Skipping empty file: {txt_file.name}")
                continue

            # Generate output filename (same name as input but .wav)
            output_file = txt_file.with_suffix(".wav")

            # Convert to audio
            save_as_audio(text, str(output_file), voice)

        except Exception as e:
            print(f"❌ Error processing {txt_file.name}: {str(e)}")

    print("\n🎉 All files processed!")

if __name__ == "__main__":
    main()

