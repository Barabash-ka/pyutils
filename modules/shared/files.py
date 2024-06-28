import tempfile
import zipfile
import tarfile
import logging
import hashlib
import os

logger = logging.getLogger(__name__)

from modules.shared.logging import setup_logging

def count_files_in_folder(folder):
    files_in_folder = 0
    for _, _, folder_files in os.walk(folder):
        files_in_folder += len(folder_files)
    return files_in_folder

def isimage(file_path) :
    #logger.info(f"isimage called for {file_path}")
    return file_path.lower().endswith(('.jpg', '.jpeg', '.png'))

def isarchive(file_path):
    if file_path.lower().endswith(('.pptx', '.kmz', '.docx')):
        return False
    return tarfile.is_tarfile(file_path) or zipfile.is_zipfile(file_path)

def extract_totemp(file_path):
    temp_dir = tempfile.mkdtemp(prefix="pyutils_")

    if tarfile.is_tarfile(file_path):
        extract_tar(file_path, temp_dir)
    elif zipfile.is_zipfile(file_path):
        extract_zip(file_path, temp_dir)

    return temp_dir

def extract_zip(zip_path, temp_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    logger.info(f"Extracted {zip_path} to temp dir: {temp_dir}")

def extract_tar(tar_path, temp_dir):
    with tarfile.open(tar_path, 'r') as tar_ref:
        tar_ref.extractall(temp_dir)
    logger.info(f"Extracted {tar_path} to temp dir: {temp_dir}")

# https://towardsdev.com/simplifying-duplicate-image-detection-across-various-sources-a-practical-guide-f530666c0de8
def get_hash_from_contents(file_path) :
    try:
        with open(file_path, "rb") as f:
            img_data = f.read()
            img_hash = hashlib.sha256(img_data).hexdigest()
            return img_hash
    except Exception as e:
        logger.error("Failed to read image file %s: %s", file_path, e)
        return None

########################################################################

test_file = "tmp/TipsForJapan.pptx"

if __name__ == "__main__":
    setup_logging(None)
    logger = logging.getLogger("files_test")

    istar = tarfile.is_tarfile(test_file) 
    iszip = zipfile.is_zipfile(test_file)
    isarchive = isarchive(test_file)
    logger.info(f"istar={istar}, iszip={iszip}, isarchive={isarchive}")

    