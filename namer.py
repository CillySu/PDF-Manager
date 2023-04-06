import os
import re
import fitz
import glob
from termcolor import colored
import sys

def rename_pdf(filename):
    file_path = os.path.abspath(filename)
    if not file_path.lower().endswith(".pdf"):
        print(f"{colored(file_path, 'red')} is not a valid PDF file.")
        return

    if "pdf" in file_path[:-4].lower():
        new_filename = filename.replace("pdf", "").replace(".pdf", "") + ".pdf"
        print(f"{colored(file_path, 'red')} contains 'pdf' in its name. Fixing.")
        return

        # Skip the file if it's empty or broken
    try:
        # Open the PDF
        pdf = fitz.open(file_path)
        pdf.close()
    except (fitz.fitz.EmptyFileError, fitz.fitz.FileDataError) as e:
        print(f"Skipping {filename} due to error: {e}")
        return

    pdf = fitz.open(file_path)
    pdf_metadata = pdf.metadata

    title = ""
    author = ""

    if "title" in pdf_metadata:
        title = pdf_metadata["title"]
    if "author" in pdf_metadata:
        author = pdf_metadata["author"]

    if not author:
        new_filename = f"{title[:50]}.pdf"
    else:
        author = author[:30]
        author = re.sub('[^A-Za-z0-9 ]+', '', author)
        author = author.title().strip()
        title = re.sub('[^A-Za-z0-9 ]+', '', title)
        title = title[:50-len(author)].strip()
        title = title.title().strip()
        new_filename = f"{author} - {title}.pdf"

    new_filename = new_filename.replace("_", " ")
    new_filename = re.sub('[^A-Za-z0-9_\-\. ]+', '', new_filename)
    new_filename = re.sub(' +', ' ', new_filename)

    # Remove superfluous suffixes
    while True:
        match = re.search(r' \(\d+\)\.pdf$', new_filename)
        if match:
            suffix_start_index, suffix_end_index = match.span()
            suffix_number_str = match.group()[2:-4]
            if int(suffix_number_str) > 1:
                new_filename = re.sub(r"\.(pdf)?", "", new_filename)
                new_filename = new_filename[:suffix_start_index] + ".pdf"
            else:
                break
        else:
            break

    if not new_filename[0].isalnum():
        new_filename = f"PDF {new_filename}"

    if len(new_filename) > 255:
        new_filename = new_filename[:255]

    new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
    suffix = 1
    while os.path.exists(new_file_path):
        new_filename = re.sub(r'\(\d+\)', '', new_filename)
        new_filename = new_filename.strip()
        new_filename = re.sub(r'(\.pdf)+$', '', new_filename)
        new_filename = f"{new_filename}({suffix}).pdf"
        new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
        suffix += 1

    os.rename(file_path, new_file_path)
    print(f"Renamed {colored(file_path, 'green')} to {colored(new_filename, 'green')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <filename(s)> or <path/to/directory>")
        sys.exit(1)

    filenames = []
    for arg in sys.argv[1:]:
        if os.path.isdir(arg):
            filenames += glob.glob(os.path.join(arg, '*.pdf'))
        elif os.path.isfile(arg):
            filenames.append(arg)
        else:
            print(f"Error: {arg} is not a valid file or directory.")
            sys.exit(1)

    for filename in filenames:
        rename_pdf(filename)
