For videos and PDFs, there are libraries in Python that can extract metadata similarly to how `ExifRead` works for images. Here’s an overview of some popular libraries and how they can be used:

### Video Metadata Extraction

For videos, you can use `moviepy` or `ffmpeg-python` to extract metadata. `ffmpeg` is a very powerful tool that can handle a wide range of multimedia files.

### PDF Metadata Extraction

For PDFs, `PyPDF2` or `pdfminer.six` can be used to extract metadata.

### Example Implementations

Here’s how you can create modules to handle metadata extraction for videos and PDFs:

#### `video_processing.py`

```python
import os
import logging
from moviepy.editor import VideoFileClip

def get_video_metadata(video_path):
    try:
        with VideoFileClip(video_path) as video:
            duration = video.duration  # duration in seconds
            size = os.path.getsize(video_path)
            return {
                'duration': duration,
                'size': size,
                'resolution': (video.w, video.h),
                'fps': video.fps
            }
    except Exception as e:
        logging.error(f"Error reading video metadata: {e}")
        return {}

def process_videos(source_dir, dest_dir):
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('.mp4', '.avi', '.mkv')):
                video_path = os.path.join(root, file)
                logging.debug(f"Processing video: {video_path}")
                metadata = get_video_metadata(video_path)
                # Add your own criteria for organizing videos
                logging.info(f"Metadata for {video_path}: {metadata}")
                # Example: move/copy the video based on metadata
                shutil.copy2(video_path, os.path.join(dest_dir, file))
                logging.info(f"Copied: {video_path} to {dest_dir}")
```

#### `pdf_processing.py`

```python
import os
import logging
import PyPDF2

def get_pdf_metadata(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            pdf = PyPDF2.PdfFileReader(f)
            info = pdf.getDocumentInfo()
            num_pages = pdf.getNumPages()
            return {
                'title': info.title,
                'author': info.author,
                'num_pages': num_pages,
                'subject': info.subject,
                'producer': info.producer,
                'creator': info.creator,
                'creation_date': info.created,
                'mod_date': info.modified
            }
    except Exception as e:
        logging.error(f"Error reading PDF metadata: {e}")
        return {}

def process_pdfs(source_dir, dest_dir):
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                logging.debug(f"Processing PDF: {pdf_path}")
                metadata = get_pdf_metadata(pdf_path)
                # Add your own criteria for organizing PDFs
                logging.info(f"Metadata for {pdf_path}: {metadata}")
                # Example: move/copy the PDF based on metadata
                shutil.copy2(pdf_path, os.path.join(dest_dir, file))
                logging.info(f"Copied: {pdf_path} to {dest_dir}")
```

### Integrating with Main Script

Now, you can update your main script (`organize_videos.py`, `organize_pdfs.py`) to utilize these processing functions. 

#### `organize_videos/organize_videos.py`

```python
import argparse
import logging
import os
import shutil

from common.logging_setup import setup_logging
from common.utils import extract_zip
from video_processing import process_videos

if __name__ == "__main__":
    setup_logging('organize_videos.log')
    
    parser = argparse.ArgumentParser(description="Process videos from a zip file and organize them by some criteria.")
    parser.add_argument('zip_file_path', type=str, help="Path to the zip file containing videos.")
    parser.add_argument('destination_directory', type=str, help="Path to the directory where organized videos will be copied.")
    args = parser.parse_args()
    
    zip_file_path = args.zip_file_path
    destination_directory = args.destination_directory
    
    logging.info(f"Starting video processing with zip file {zip_file_path} and destination directory {destination_directory}")
    
    extracted_dir = extract_zip(zip_file_path)
    
    try:
        process_videos(extracted_dir, destination_directory)
    finally:
        shutil.rmtree(extracted_dir)
        logging.info(f"Removed temporary directory {extracted_dir}")
    
    logging.info("Video processing completed")
```

#### `organize_pdfs/organize_pdfs.py`

```python
import argparse
import logging
import os
import shutil

from common.logging_setup import setup_logging
from common.utils import extract_zip
from pdf_processing import process_pdfs

if __name__ == "__main__":
    setup_logging('organize_pdfs.log')
    
    parser = argparse.ArgumentParser(description="Process PDFs from a zip file and organize them by some criteria.")
    parser.add_argument('zip_file_path', type=str, help="Path to the zip file containing PDFs.")
    parser.add_argument('destination_directory', type=str, help="Path to the directory where organized PDFs will be copied.")
    args = parser.parse_args()
    
    zip_file_path = args.zip_file_path
    destination_directory = args.destination_directory
    
    logging.info(f"Starting PDF processing with zip file {zip_file_path} and destination directory {destination_directory}")
    
    extracted_dir = extract_zip(zip_file_path)
    
    try:
        process_pdfs(extracted_dir, destination_directory)
    finally:
        shutil.rmtree(extracted_dir)
        logging.info(f"Removed temporary directory {extracted_dir}")
    
    logging.info("PDF processing completed")
```

### Conclusion

By using specialized libraries for different file types, you can extract metadata from videos and PDFs in a similar way to images. This allows you to organize and process these files effectively. The modular structure helps in maintaining and extending the functionalities for different types of files.