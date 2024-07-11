import argparse
import logging
import os
import shutil
import glob
import time

#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#print(parent_dir)
#import sys
#sys.path.append(parent_dir)

import modules.shared.myfile as myfile
import modules.img.img as img
from modules.geoloc.geoloc_cache import GeolocationCache
from modules.shared.mylog import setup_logging

# Globals
program_name = "photos_organizer"
program_abbr = "photos"
program_description = '''\
        Ogranize your photos for easy storage and browsing!!!
        -----------------------------------------------------
        photos_organizer processes image files located in <source>: 
        - retrieves date and location information for each image file, 
        - creates new names based on date and location infromation,
        - copies renamed image files into subfolders in <destination> folder, one subfolder for each year.
        -----------------------------------------------------
        '''
moto = "Smile and love, always!!! Kathy :-)"
logger = logging.getLogger(program_abbr)
loglevel = logging.INFO
shutup_modules= [
    ("PIL",logging.ERROR),
    ("exif",logging.ERROR),
    ("exifread",logging.ERROR),
    #("modules.img.img",logging.WARNING),
    ("modules.img.img",logging.DEBUG),
    ("modules.img.img_exif",logging.WARNING),
    ("modules.img.img_exifread",logging.WARNING),
    ("modules.shared.mydate",logging.WARNING),
    #("modules.shared.mydate",logging.DEBUG),
]
NO_YEAR = "NoYear"
NO_DATE = "NoDate"
NO_LOC = "NoLoc"
SUBDIR_OTHER = "Other"

def decide_for_duplicates(src_path, dst_path, ext):
    src_hash = myfile.get_hash_from_contents(src_path)
    dst_hash = myfile.get_hash_from_contents(dst_path)
    
    if src_hash == dst_hash: 
        logger.debug(f"file with same name and contents exists in destination, no need to copy")
        return None

    # get all potential duplicates at destination
    glob_pattern = f"{dst_path[0:len(dst_path)-len(ext)]}*"
    logger.debug(f"glob_pattern={glob_pattern}")
    glob_files = glob.glob(glob_pattern)
    logger.debug(f"before hash comparison: considering {len(glob_files)} files")
    for file in glob_files:
        if not file.lower().endswith(ext.lower()):
            logger.debug(f"removing file from glob_files: {file}")
            glob_files.remove(file)
            continue
        hash = myfile.get_hash_from_contents(file)
        if hash == src_hash:
            logger.debug(f"file with same contents in destination, no need to copy: {file}")
            return None
    
    logger.debug(f"compute alt name considering {len(glob_files)} files")    
    current_max = 0
    for file in glob_files:
        name = file[0:len(file)-len(ext)]
        logger.debug(f"file={file}, name={name}") 
        try:
            num  = int(name.split('-')[-1])
            if num > current_max:
                current_max = num
            logger.debug(f"num={num}, current_max={current_max}") 
        except :
            continue
    logger.debug(f"current_max={current_max}")
    return (current_max + 1)

def copy_from_src_to_dst(files_at_scr, files_at_dst, dst_dir):
    copied = skipped = 0

    for src_path in files_at_scr:
        logger.info(f"start processing: {src_path}")
        subdir, file, extension = compute_dst_name(src_path)
        dst_subdir = os.path.join(dst_dir, subdir)
        os.makedirs(dst_subdir, exist_ok=True)
        dst_path = f"{os.path.join(dst_subdir, file)}{extension}"
        logger.info(f"destination path: {dst_path}")
    
        if dst_path in files_at_dst:
            alt_file_num = decide_for_duplicates(src_path, dst_path, extension)
            if alt_file_num:
                alt_file = f"{file}-{alt_file_num}"
                dst_path = f"{os.path.join(dst_subdir, alt_file)}{extension}"
                logger.info(f"alt destination: {dst_path}")                

        if dst_path not in files_at_dst:
            shutil.copy2(src_path, dst_path)
            copied += 1
            files_at_dst.append(dst_path)
            logger.info(f"copied from {src_path} to {dst_path}")
        else:
            skipped += 1
            logger.info(f"skipped as duplicate")
            continue
        
    return copied, skipped

def compute_dst_name(src_path):
    scr_basename = os.path.basename(src_path)
    src_filename, src_extension = os.path.splitext(scr_basename)

    dst_filename = src_filename
    dst_extension = src_extension.lower()
    dst_subdir = SUBDIR_OTHER
    if img.isimage(src_path) :
        year_taken, date_taken, loc_taken = img.get_image_metadata(src_path, geocache)
        dst_subdir = str(year_taken)
        dst_filename = f"{date_taken}_{loc_taken}"

    logger.debug(f"\ndst_subdir={dst_subdir} of type {type(dst_subdir)} \
                \ndst_filename={dst_filename} of type {type(dst_filename)}\
                \ndst_extension={dst_extension} of type {type(dst_extension)}")
    return dst_subdir, dst_filename, dst_extension

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog = program_name,
        formatter_class = argparse.RawDescriptionHelpFormatter, 
        description=program_description, 
        epilog = moto)
    
    parser.add_argument(
        '-s',
        '--src', 
        type = str, 
        metavar = 'SRC',
        default = '.',
        help= "Path to the source location")
    
    parser.add_argument(
        '-d', 
        '--dst',
        type=str, 
        metavar = 'DST',
        default = './photo_organizer_out',
        help="Path to the directory where organized images will be copied")
    
    parser.add_argument(
        '--keep-temp', 
        action='store_true', 
        help="Keep the temporary directory after processing")
    
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help="Run with debug logging")
    
    args = parser.parse_args()

    if args.debug:
        loglevel = logging.DEBUG
    setup_logging(f"{program_name}.log", log_level=loglevel, shutup_modules=shutup_modules)

    src = os.path.abspath(args.src)
    dst = os.path.abspath(args.dst)
    keep_temp = args.keep_temp
    logger.info(f"Called to sort through files in {src}: dst = {dst}; keep_temp = {keep_temp}")
    os.makedirs(dst, exist_ok=True)
    #non_img_subfolder = f"{dst}{os.sep}Other"
    #os.makedirs(non_img_subfolder, exist_ok=True)
    
    files_at_src = []
    tempdirs_for_src = []
    start = time.time()
    myfile.all_files_at_path(src, files_at_src, tempdirs_for_src)
    num_files_at_src = len(files_at_src)
    num_temp_dirs = len(tempdirs_for_src)
    end = time.time()
    logger.info(f"Collected {num_files_at_src} files at source while opening {num_temp_dirs} archives in {(end-start):.2f} seconds")
    #logger.debug(f"files_at_scr={files_at_src}, tempdirs_for_src={tempdirs_for_src}")

    files_at_dst = []
    tempdirs_for_dst = []
    start = time.time()
    myfile.all_files_at_path(dst, files_at_dst, tempdirs_for_dst)
    dst_files_before = len(files_at_dst)
    num_dst_archives = len(tempdirs_for_dst)
    end = time.time()
    logger.info(f"Collected {dst_files_before} files at destination while opening {num_dst_archives} archives in {(end-start):.2f} seconds")
    #logger.debug(f"files_at_dst={files_at_dst}, tempdirs_for_dst={tempdirs_for_dst}")
    if num_dst_archives :
        logger.warning(f"Archived files at destination may result in duplicates")
         
    geocache = GeolocationCache()
    locations = geocache.get_size()
    logger.info(f"Initialized geolocation cache with {locations} entries")

    start = time.time()
    logger.info(f"STARTED with {num_files_at_src} files at source and {dst_files_before} files at destination")
    try:
        copied, skipped = copy_from_src_to_dst(files_at_src, files_at_dst, dst)
    except Exception as e:
        logger.error(f"SOMETHING WENT WRONG: {e}", exc_info=1)
    end = time.time()
    dst_files_after1 = len(files_at_dst)
    logger.info(f"COMPLETED in {(end-start):.2f} seconds with {dst_files_after1} files at destination")
    files_at_dst = []
    myfile.all_files_at_path(dst, files_at_dst, [])
    dst_files_after2 = len(files_at_dst)
    logger.info(f"\nSUMMARY: \
                \nSRC-check: \
                \n\tTotal files                 : {num_files_at_src} \
                \n\tCopied files                : {copied} \
                \n\tSkipped files               : {skipped} \
                \n\tCopied + Skipped files      : {copied + skipped} \
                \nDST-check: \
                \n\tBefore                      : {dst_files_before} \
                \n\tAfter (internal counter)    : {dst_files_after1} \
                \n\tAfter (before plus copied)  : {dst_files_before+copied} \
                \n\tAfter (real)                : {dst_files_after2} \
                \nAdded {geocache.get_size()-locations} places to the geolocations cache.")
    if keep_temp:
        logger.info(f"List of preserved temporary folders:\n{tempdirs_for_src}")
