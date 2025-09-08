
import os
from pathlib import Path
# with os.path.walk
def delete_backups(arg, dirname, names):
    for name in names:
        if name.endswith('~'):
            os.remove(os.path.join(dirname, name))

# os.path.walk(os.environ['HOME'], delete_backups, None)

# with os.path, if (like me) you can never remember how os.path.walk works
def walk_tree_delete_backups(dir):
    for name in os.listdir(dir):
        path = os.path.join(dir, name)
        if os.path.isdir(path):
            walk_tree_delete_backups(path)
        elif name.endswith('~'):
            os.remove(path)

# walk_tree_delete_backups(os.environ['HOME'])

# with path
# dir = Path(os.environ['HOME'])
# dir = Path('d')
# print(f"dir={dir}")
# for f in dir.walk():
#     print(f"file: {f}")
#     if f.isfile():
#         print(f"file: {f}")

from datetime import datetime
from collections import Counter

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

from pprint import pprint
# from inspect import getmembers
# from types import FunctionType

# def attributes(obj):
#     disallowed_names = {
#       name for name, value in getmembers(type(obj)) 
#         if isinstance(value, FunctionType)}
#     return {
#       name: getattr(obj, name) for name in dir(obj) 
#         if name[0] != '_' and name not in disallowed_names and hasattr(obj, name)}

# def print_attributes(obj):
#     pprint(attributes(obj))

mydir = Path.cwd().parent
pprint(f"mydir={mydir}")
mydir_type = type(mydir)
pprint(f"mydir_type={mydir_type}")
pprint(f"mydir_dir={mydir.__dir__()}")
pprint(dir(mydir))
pprint(vars(mydir.stat()))
print(f"dir: {mydir}, \nstat: {mydir.stat()}, \nobj: {mydir.__dir__}")
print("All attributes and methods:", mydir.__dir__())
# print("Attributes and methods of example_object:", dir(mydir))

by_ext = Counter(path.suffix for path in mydir.iterdir())
print(by_ext)

by_time = Counter(datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d") for path in mydir.iterdir())
print(by_time)

# for f in dir.walk():
#     print(type(f), f)
#     # if f.isfile():
#     #     print(f"file: {f}, {f.stat()}")

# datetime.fromtimestamp(time)
# for f in dir..iterdir():
#     print(f"file: {f}, {f.stat()}")
#     # time, file_path = max(f.stat().st_mtime, f) 
#     # print(f"file: {f}, file_path: {file_path}, time: {time}")
