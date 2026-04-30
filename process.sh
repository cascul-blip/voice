#!/bin/bash
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

if [[ -f "$1" ]]; then
    echo "✅ Success: $1 is an existing file."
else
    echo "❌ Failure: $1 does not exist or is not a regular file."
    exit 1
fi

#Remove and recreate the chapters directory
rm -rf chapters
mkdir chapters

#Split the epub into text files by chapter
python epub_to_chapters.py $1
cd chapters

for file in *; do
    # Check if the item is a file (and not a directory)
    if [ -f "$file" ]; then
        # echo "Processing $file ===> $voice_choice"
        python ../batch.py "$file" "$voice_choice"
        echo "󱔸 Processed the file, waiting for cooldown..."
        sleep 2
    fi
done
cd ..

# NEXT -- MOVE TO A FOLDER AND CONVERT
echo "󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈󰗈"
echo "Proccessing into wav files completed."


# 1. Prompt and capture input safely
read -p "What directory should this be placed in?:" user_input_dir

echo "Entered '$user_input_dir'"

# 2. Check for empty input (Using the variable name instead of 'lin')
if [ -z "$user_input_dir" ]; then
   echo "Directory not entered, skipping conversion."
   exit 1
fi

# Define the path we want to work in
TARGET_DIR="./$user_input_dir"

# 3. Attempt to create the directory AND check for errors (The critical fix)
if mkdir -p "$TARGET_DIR"; then
    echo "Successfully created/verified directory: $TARGET_DIR"
else
    # This block runs ONLY if mkdir fails (e.g., permissions denied, invalid path)
    echo "ERROR: Could not create directory '$user_input_dir'. Check permissions or name validity."
    exit 1
fi

# 4. Change directory only IF the previous commands succeeded
if cd "$TARGET_DIR"; then
    echo "Successfully moved into directory: $(pwd)" # Prints the full path of the current working directory
else
    # This handles failure during the 'cd' step (very rare, but good practice)
    echo "CRITICAL ERROR: Failed to change into '$user_input_dir'."
    exit 1
fi

cp ../chapters/*.wav .
for file in *.wav; do ffmpeg -i "$file" -b:a 32k "${file%.wav}.mp3"; done
rm *.wav
