## Metadata

## Image Metadata

[`ExifRead`](exif.md) can both read and update image metadata

## Video Metadata

For videos, you can use `moviepy` or `ffmpeg-python` to extract metadata. `ffmpeg` is a very powerful tool that can handle a wide range of multimedia files.

#### Example 

```python
# `video_processing.py`
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


## PDF Metadata

`PyPDF` - very well documented and maintained package
    [package](https://pypi.org/project/pypdf/)
    [docs](https://pypdf.readthedocs.io/)
`pdfminer.six` 

### Example 

```python
# `pdf_processing.py`
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

## Conclusion

By using specialized libraries for different file types, you can extract metadata from videos and PDFs in a similar way to images. This allows you to organize and process these files effectively. The modular structure helps in maintaining and extending the functionalities for different types of files.