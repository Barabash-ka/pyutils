import tempfile
import zipfile
import tarfile
import logging
import hashlib
import os
import shutil

logger = logging.getLogger(__name__)

from modules.shared.mylog import setup_logging

def all_files_at_path(path, files_at_path, tempdirs_for_path, hashtable) :
    logger.debug(f"start collecting all the files at {path} with {len(files_at_path)} files and {len(hashtable)} unique hashes")
    if os.path.isdir(path):
        logger.debug(f"{path} is a directory, walk through the entries")
        dirEntries = os.scandir(path)
        for entry in dirEntries :
            all_files_at_path(os.path.join(path, entry.name), files_at_path, tempdirs_for_path, hashtable)
        dirEntries.close()
    elif os.path.isfile(path):
        logger.debug(f"{path} is a file, see whether it is an archive")
        if isarchive(path):
            logger.debug(f"{path} is an archive")
            temp_dir = extract_totemp(path)
            tempdirs_for_path.append(temp_dir)
            all_files_at_path(temp_dir, files_at_path, tempdirs_for_path, hashtable)           
        else:
            logger.debug(f"{path} is a simple file, adding")
            files_at_path.append(path)
            hash = get_hash_from_contents(path)
            if hash in hashtable:
                files = hashtable[hash]
                files.append(path)
            else:
                logger.debug(f"hash is not in the table")
                files = [path]
                hashtable[hash] = files
            
    else:
        logger.warning(f"{path} is neither a folder nor a file, skipping")

def count_files_in_folder(folder):
    files_in_folder = 0
    for _, _, folder_files in os.walk(folder):
        files_in_folder += len(folder_files)
    return files_in_folder

def isarchive(file_path):
    if file_path.lower().endswith(('.pptx', '.kmz', '.docx')):
        return False
    return tarfile.is_tarfile(file_path) or zipfile.is_zipfile(file_path)

def extract_totemp(archive_path):
    temp_dir = tempfile.mkdtemp(prefix="pyutils_")

    if tarfile.is_tarfile(archive_path):
        extract_tar(archive_path, temp_dir)
    elif zipfile.is_zipfile(archive_path):
        extract_zip(archive_path, temp_dir)

    return temp_dir

def extract_flat(archive_path, dest_path):
    logger.info(f"extract_flat entered with archive_path={archive_path}, dest_path={dest_path}")
    temp_dir = extract_totemp(archive_path)
    os.makedirs(dest_path, exist_ok=True)

    files = 0
    for _, _, folder_files in os.walk(temp_dir):
        for file_path in folder_files:
            shutil.copy2(file_path, dest_path)
            files += 1
    shutil.rmtree(temp_dir)
    
    logger.info(f"extract_flat copied {files} files")
    return files

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

def test_if_zip(test_file):
    
    logger.info(f"Testing test_if_zip for {test_file}")
    istar = tarfile.is_tarfile(test_file) 
    iszip = zipfile.is_zipfile(test_file)
    isarchive = isarchive(test_file)
    logger.info(f"Result: istar={istar}, iszip={iszip}, isarchive={isarchive}")

import time
import json
if __name__ == "__main__":
    shutup_modules= []
    setup_logging(log_level=logging.INFO, shutup_modules=shutup_modules)
    logger = logging.getLogger("myfile")

    #test_file = "tmp/TipsForJapan.pptx"
    #test_if_zip(test_file)
    #extract_flat("../tmp/Private.zip", "../tmp/out")

    testdirs = [
        "D:\\photos_by_year\\",
        #"D:\\tmp\\test",
        "D:\\tmp\\imgs_arch",
        "D:\\tmp\\fromPicLib",
    ]
    dups_file = "data/dups1.json"
    dups_hash = {}

    
    for testdir in testdirs:
        files = []
        tempdirs = []
        hashtable = {} 
        start = time.time()
        logger.info(f"TEST for {testdir}")
        all_files_at_path(testdir, files, tempdirs, hashtable = hashtable)
        num_files = len(files)
        num_unique_files = len(hashtable)
        num_tempdirs = len(tempdirs)
        num_dups = 0
        for hash, files in hashtable.items():
            num_files = len(files)
            if num_files > 1:
                names = []
                for file in files:
                    basename = os.path.basename(file)
                    if basename not in names:
                        names.append(basename)
                unique_names = len(names)
                logger.info(f"file duplicated {num_files} times with {unique_names} different basenames")
                if unique_names > 1:
                    num_dups += 1
                    dups_hash[hash] = files
        
        end = time.time()
        logger.info(f"COMPLETED in {(end-start):.2f} seconds: \
                    \n\tTotal files     : {num_files} \
                    \n\tUnique files    : {num_unique_files} \
                    \n\tArchives        : {num_tempdirs} \
                    \n\tDups diff names : {num_dups}")
    
    with open(dups_file, 'w', encoding='utf-8') as f:
        json.dump(dups_hash, f, ensure_ascii=False, indent=4)
    

    