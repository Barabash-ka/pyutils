# Pyutils package

Provides various useful programs written in python to streamline and somewhat automate digital life.

## Running the utilities

Runnable utilities are in the cli/ folder and should be run from the package root folder.
See [`cli/README`](cli/README.md) for details about available programs and their usage.

## Directory Structure

```
pyutils/
│
├── README.md               # this file
├── .gitignore   
├── __init__.py             
| 
├── cli/                    # runnable programs
│   ├── __init__.py
|   ├── photos_organizer.py
|
├── data/
│   ├── logging.py          # configure logging
│   └── files.py            # generic file handling
│
├── docs/                   # reference material
│   ├── sort_my_photos.py
│   ├── exif_extraction.py
│   ├── geocoding.py
│   ├── image_processing.py
|
├── logs/                   # program logs written here, not tracked
|
├── modules/                # program modules by category and their tests
│   ├── __init__.
│   ├── img/                # code working with images
|   |   ├── __init__.py
│   ├── video/              # code working with videos
|   |   ├── __init__.py
│   ├── pfd/                # code working with pdfs
|   |   ├── __init__.py
│   ├── shared/             # generic modules used accross the codebase
|   |   ├── __init__.py
│   ├── geoloc/             # geolocation
|   |   ├── __init__.py

