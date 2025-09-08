from pathlib import Path
import logging
import datetime
import json
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("")

start_dir_name = "D:\\"
# start_dir_name = "."
res_file_stem = 'all_by_date'

files_count = 0
min_date = datetime.date.today()
max_date = None

exclude_ext = ['.pyc']
exclude_dir = set(['.env', '.venv', '.git'])

def files_by_date_walk(top):
    for root, dirs, files in os.walk(top, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dir]
        files = [file for file in files if os.path.splitext(file)[1] not in exclude_ext]
        for file in files:
            print(file)


def string_to_record(path: Path):
    logger.info(f"\n\nstring_to_record entered for {path}")
    res = None

    try:
        if path.is_file():
            path_string = str(path)
            if not 'env' in path_string:
                base_name = path.name.encode('utf-8', 'replace').decode()
                stem = path.stem
                ext = path.suffix
                logger.info(f"base_name={base_name}, stem={stem}, ext={ext}")
                if not base_name.startswith('$'):
                    if not ext in exclude_ext:
                        res = path_string
    except Exception as e:
        logger.error(e)
        # raise e

    logger.info(f"string_to_record returns {res}")
    return res

def files_by_date_glob(start_path: Path):
    files_by_date = {}
    for path in start_path.rglob("*"):
        value_to_record = string_to_record(path)
        if not value_to_record:
            logger.info(f"skipping path={path}")
            continue

        # skipped directories and deleted files
        date_modified = datetime.date.fromtimestamp(path.stat().st_mtime)
        files_by_date_key = date_modified.strftime("%Y-%m-%d")
        
        if files_by_date_key not in files_by_date:
            # print(f"creating list for {date_modified}")
            if min_date > date_modified:
                min_date = date_modified
            if not max_date or max_date < date_modified:
                max_date = date_modified
            files_by_date[files_by_date_key] = {'date': files_by_date_key, 'date_year': date_modified.year, 'date_month' : date_modified.month, 'date_day' : date_modified.day, 'files': []}
        files_by_date.get(files_by_date_key)['files'].append(value_to_record)
        files_count += 1
        
    return files_by_date

start_path = Path(start_dir_name).absolute()
if not start_path.is_dir():
    logger.info(f"{start_path} is not a directory")
    sys.exit()
files_by_date = files_by_date_glob(start_path)
print(f"Processed {start_path}:\nfound {files_count} files for {len(files_by_date)} days, starting with {min_date} and ending with {max_date}")
# print(json.dumps(files_by_date, indent=2, sort_keys=True))

sorted_by_date = dict(sorted(files_by_date.items()))

def dump_batch(batch_number, batch):
    print(f"dump_batch: batch_number = {batch_number}")
    batch_file = res_file_stem + str(batch_number) + '.json'
    with open(batch_file, 'w') as f:
        json.dump(batch, f, indent=2) 

batch = []
batch_number = 1
batch_size = 30
batch_count = 0
for item in sorted_by_date.values():
    print(f"batch_count={batch_count}")
    batch.append(item)
    batch_count += 1
    if batch_count == batch_size:
        dump_batch(batch_number, batch)
        batch = []
        batch_number += 1
        batch_count = 0
dump_batch(batch_number, batch)   
    

# to_print = []
# for i in range(30):
#     sorted_files_by_date[i]
# with open(res_file, 'w') as f:
#     json.dump(sorted_files_by_date, f, indent=2)
