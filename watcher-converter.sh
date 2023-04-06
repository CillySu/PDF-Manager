#!/bin/bash

#Set these to your desired paths
WATCH_DIR="/mnt/wd/moodle-dl" # The script watches for files which are modified or moved to this location
DEST_DIR="/mnt/wd/consume" # The script places files here after either converting Office files from the WATCH_DIR to PDF, or after a PDF populates WATCH_DIR
RENAME_DEST_DIR="/mnt/wd/consume" # The directory where the script places files after renaming them
PROCESSED_FILE="/mnt/wd/services/mdl-watcher/processed_files.txt"

# Watch for new files in $WATCH_DIR
inotifywait -m -r -q --format '%w%f' -e create,moved_to "$WATCH_DIR" |
while read FILENAME
do
  if [[ "${FILENAME,,}" =~ \.(doc|docx|xls|xlsx|ppt|pptx|pdf)$ ]]; then
    echo "Found new file: \"$FILENAME\""
    # Check if the file has been processed before
    if grep -qFx "$(basename "$FILENAME")" "$PROCESSED_FILE"; then
      echo "Skipping \"$FILENAME\" (already processed)"
    else
      # Check if the file is an office file
      if [[ "${FILENAME,,}" =~ \.(doc|docx|xls|xlsx|ppt|pptx)$ ]]; then
        echo "Converting \"$FILENAME\" to PDF"
        # Convert the office file to PDF using LibreOffice
        libreoffice --headless --convert-to pdf --outdir "$DEST_DIR" "$FILENAME"
      else
        echo "Moving \"$FILENAME\" to \"$DEST_DIR\""
        # Move the PDF file to $DEST_DIR
        mv "$FILENAME" "$DEST_DIR"
      fi
      # Record the processed file in the processed_files.txt file
      echo "$(basename "$FILENAME")" >> "$PROCESSED_FILE"
    fi
  fi
done &

while true; do
      inotifywait -q -m -e create --format '%f' "${RENAME_DEST_DIR}" | while read FILENAME; do
    if [[ "${FILENAME}" == *.pdf ]]; then
      python3 /mnt/wd/shell-scripts/pdf-namer.py "${RENAME_DEST_DIR}/${FILENAME}"
    fi
  done
done
