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
echo "✅ Success: $1 is an existing file."

#Remove and recreate the chapters directory
rm -rf chapters
mkdir chapters

# Split the epub into text files by chapter
python epub_to_chapters.py "$1"

for file in chapters/*; do
    # Check if the item is a regular file and not a directory
    if [ -f "$file" ]; then
        echo "Processing $(basename "$file") ===> $voice_choice"
        python batch.py "$file" "$voice_choice"
        echo "󱔸 Processed the chapter, waiting for cooldown..."
        sleep 2
    fi
done

echo "󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈"
echo "Proccessing into wav files completed."
read -p "What directory should this be placed in?:" user_input_dir

if [ -z "$user_input_dir" ]; then
   echo "Directory not entered, skipping conversion."
   exit 1
fi

TARGET_DIR="./$user_input_dir" # Use local pathing relative to script execution location

if ! mkdir -p "$TARGET_DIR"; then
    echo "ERROR: Could not create directory '$user_input_dir'. Check permissions or name validity."
    exit 1
fi
echo "Successfully created/verified directory: $TARGET_DIR"

# Perform all subsequent operations inside the target directory context without using 'cd' for movement.
# Use subshell execution or explicit relative pathing to maintain script safety and clean state.

echo "Moving into '$user_input_dir' context for final processing..."

# Copy files from chapters directly into the new TARGET_DIR
cp -v ../chapters/*.wav "$TARGET_DIR"/ 2>/dev/null || { echo "Warning: No .wav files found in ../chapters."; }

# Iterate over WAV files located *within* the target directory
for file in "$TARGET_DIR"/*.wav; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "Converting $filename to MP3..."
        ffmpeg -i "$file" -b:a 32k "${file%.wav}.mp3"
    fi
done

# Clean up original WAV files from the target directory
rm -v "$TARGET_DIR"/*.wav 2>/dev/null || { echo "No .wav files to clean up in $TARGET_DIR."; }

echo "✅ Conversion process completed successfully within '$user_input_dir'."
