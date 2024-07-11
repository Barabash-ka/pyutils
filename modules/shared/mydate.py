import logging
import os
from datetime import datetime
import dateparser
from dateutil import parser

import modules.shared.mylog as mylog

logger = logging.getLogger(__name__)

def pick_earliest_date(dates, min_date = None, max_date = None):
    if not dates or not len(dates):
        return None
    
    if max_date and min_date and max_date < min_date:
        logger.warning(f"wrong input for dates={dates}, max_date={max_date}, min_date={min_date}")
        return None
    
    dates.sort()   
    result = dates[0]
    if min_date:
        for date in dates:
            if date > min_date:
                if max_date and date < max_date:
                    result = date
                break
    logger.debug(f"{result} is min date for dates={dates}, max_date={max_date}, min_date={min_date}")
    return result
    
def datetime_from_string(datestring, datefmts):
    dt = None

    for fmt in datefmts:
        try:
            dt = datetime.strptime(datestring, fmt)
            break
        except Exception as e:
            logger.debug(f"strptime failed to extract date from {datestring}, e={e}") 
            continue

    if not dt:
        try:
            dt = parser.parse(datestring)
        except Exception as e:
            logger.debug(f"parser failed to extract date from {datestring}, e={e}") 
    
    # silenced as it was not usefull
    # if not dt:
    #     try:
    #         dt = dateparser.parse(datestring)
    #     except Exception as e:
    #         logger.debug(f"dateparser failed to extract date from {datestring}, e={e}")     

    if dt:
        logger.debug(f"extracted date {dt} from string {datestring}")    
    return dt

def datetime_from_os(file):
    result = None
    
    os_times = []
    ctime = datetime.fromtimestamp(os.path.getctime(file))
    os_times.append(ctime)
    atime = datetime.fromtimestamp(os.path.getatime(file))
    os_times.append(atime)
    mtime = datetime.fromtimestamp(os.path.getmtime(file))
    os_times.append(mtime)
    
    if len(os_times):
        os_times.sort()
        result = os_times[0]

    logger.debug(f"datetime from os: {result}") 
    return result

def datetime_from_file(file, min_date = None, max_date = datetime.now()):
    dates = [datetime_from_os(file)]

    filename, _ = os.path.splitext(os.path.basename(file))
    date = dateparser.parse(filename)
    if date:
        logger.debug(f"date from dateparser: {date} of type {type(date)}")
        dates.append(date)

    filename = ''.join(filename.split('_'))
    filename = ''.join(filename.split('-'))
    filename = ''.join(filename.split(' '))
    name_len = len(filename)
    logger.debug(f"string reduced from the file name: {filename} with {name_len} chars")
    
    date_len = 8
    fmts = ['%d%m%Y', '%Y%m%d', '%m%d%Y']
    i = 0
    while i <= name_len-date_len:
        test_str = filename[i:i+date_len]
        i += 1

        if not test_str.isdigit():
            continue
        
        date = datetime_from_string(test_str, fmts)
        if date:
            dates.append(date)
            
    date = pick_earliest_date(dates, min_date=min_date, max_date=max_date)
    return date

#############################################################

testdir = "D:\\tmp\\test\\"

shutup_modules= [
    ("tzlocal",logging.ERROR),
]

import os
if __name__ == "__main__":
    mylog.setup_logging(log_level=logging.DEBUG, shutup_modules=shutup_modules)
    logger = logging.getLogger("mydate")

    tests = os.listdir(testdir)
    for test in tests:
        test = os.path.join(testdir, test)
        logger.info(f"TEST IMAGE: {test}")
        dt = datetime_from_file(test)
        logger.info(f"RESULT: dt={dt}, type={type(dt)}")