from typing import List, Tuple
import re
import os
import enum

# Importer parameters
from defaults import *
from utils import *

class FileClass(enum.Enum):
    UNKNOWN = 0
    PHOTO = 1
    VIDEO = 2

def isSimplePhoto(a_file) -> bool:
    # Match name formats: 
    # * PXL_12345678_123456789.jpg
    # * PXL_12345678_123456789.NIGHT.jpg
    # * PXL_12345678_123456789.LONG_EXPOSURE-02.ORIGINAL.jpg
    m = re.fullmatch(r"^PXL_\d+_\d+(~\d+)?(\.[\w\_\-]+)*\.jpg$", a_file)
    if not m:
        return False
    return True

def isSimpleVideo(a_file) -> bool:
    # Match name formats:
    # * PXL_12345678_123456789.mp4
    # * PXL_12345678_123456789.TS.mp4
    m = re.fullmatch(r"^PXL_\d+_\d+(~\d+)?(\.[\w\_\-]+)*\.mp4$", a_file)
    if not m:
        return False
    return True

# Extract the date from a folder name formatted as YYYY-MM-DD with an optional description
# Returns the date as YYYYMMDD
def GetDateFromFolderName(a_folder_name: str) -> str:
    # Pattern matches dates (YYYY-MM-DD) optionally followed by a description.
    # Examples: 2023-05-20, 2023-05-20_Party, 2023-05-20-Trip
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})(?:[_-][\w\-]*)?$", a_folder_name)
    if m:
        return "".join(m.groups())
    return ""

def ClassifyOneFile(a_file) -> Tuple[str, FileClass]:
    c = FileClass.UNKNOWN
    if isSimplePhoto(a_file):
        c = FileClass.PHOTO
    elif isSimpleVideo(a_file):
        c = FileClass.VIDEO
    return (a_file, c)

def ClassifyPhotos(a_file_or_dir) -> List[Tuple[str, FileClass]]:
    r = []
    if os.path.isdir(a_file_or_dir):
        all_files = GetSourceFiles(a_file_or_dir)
        for current_file in all_files:
            r.append(ClassifyOneFile(current_file))
    else:
        r.append(ClassifyOneFile(a_file_or_dir))
    return r

def main():
    source_dir = default_stage_dir
    r = ClassifyPhotos(source_dir)
    list(map(lambda x: print(x[0], x[1]), r) )

if __name__ == "__main__":
    main()
