import argparse
import logging
import os
import shutil

from shared.logging_setup import setup_logging
from shared.utils import extract_zip
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