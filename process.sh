#!/bin/bash
set -euo pipefail # Exit on error, treat unset variables as errors, and fail pipeline if any command fails
#This is the master script that will convert the e-book into mp3 files.  You *should* just have to run this.


#If no argument passed
if [ -z "$1" ]; then
  echo "Usage: process.sh <filename>"
  exit 1
fi


# Option to change the voice
read -p "Enter voice name (press Enter for am_michael): " voice_choice
if [ -z "$voice_choice" ]; then
    voice_choice="am_michael"
fi

# Check if the file exists before proceeding
if [ ! -f "$1" ]; then
    echo "❌ Failure: '$1' does not exist or is not a regular file. Please check the path."
    exit 1
fi

#Remove and recreate the chapters directory
rm -rf chapters
mkdir chapters

# Split the epub into text files by chapter
echo -e "────────── \033[1m Splitting chapters from the epub file \033[0m ────────────────────"
python epub_to_chapters.py "$1"
echo -e "────────── \033[1m Kokoro AI converting text to audio \033[0m ───────────────────────"
for file in chapters/*; do
    # Check if the item is a regular file and not a directory
    if [ -f "$file" ]; then
        python batch.py "$file" "$voice_choice"
        sleep 2
    fi
done

echo -e "────────── \033[1m Transcription complete \033[0m ───────────────────────────────────"
read -p "What directory do you want to save the mp3 files to?:" user_input_dir

if [ -z "$user_input_dir" ]; then
   echo "Directory not entered, skipping conversion."
   exit 1
fi

TARGET_DIR="./$user_input_dir" # Use local pathing relative to script execution location

if ! mkdir -p "$TARGET_DIR"; then
    echo "ERROR: Could not create directory '$user_input_dir'. Check permissions or name validity."
    exit 1
fi

# Copy files from chapters directly into the new TARGET_DIR
cp ./chapters/*.wav "$TARGET_DIR"/ 2>/dev/null || { echo "Warning: No .wav files found in ./chapters."; }

for file in "$TARGET_DIR"/*.wav; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo -e "Converting $file to .mp3"
        ffmpeg -v 16 -i "$file" -b:a 32k "${file%.wav}.mp3"
    fi
done

# Clean up original WAV files from the target directory
rm -v "$TARGET_DIR"/*.wav 2>/dev/null || { echo "No .wav files to clean up in $TARGET_DIR."; }

echo "✅ Conversion process completed successfully within '$user_input_dir'."
notify-send "TTS Complete!"
