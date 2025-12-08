import os
import shutil
import sys

# Supporting libraries
from PIL import Image

# Importer parameters
from defaults import *
from utils import *


# def ClearDir(a_dir):
#     if a_dir != dest_dir:
#         print("Not clearing non-test dir", a_dir)
#         return
#     try:
#         files = os.listdir(a_dir)
#         for file in files:
#             file_path = os.path.join(a_dir, file)
#             if os.path.isfile(file_path):
#                 os.remove(file_path)
#         print("Destination dir", a_dir, "cleared.")
#     except OSError:
#         print("Error occured clearing dir", a_dir)


def QualifyFileSize(a_file):
    # File too small
    # Default threshold is 100KB. Genuine files as small as 150KB have been found.
    size_threshold = 100*1024
    if os.path.getsize(a_file) < size_threshold:
         return {"qualified": False, "reason": "Size under threshold of " + f"{size_threshold:,}"}
    
    return {"qualified": True, "reason": ""}

# Extract the file date from PXL_########_#########_???.jpg
def GetFileDate_PXL(a_filename):
    parts = a_filename.split('_')
    # There must be at least 3 parts
    if len(parts) < 3:
        return ""
    file_date_str = parts[1]
    if len(file_date_str) != 8:
        return ""
    return file_date_str[:4] + "-" + file_date_str[4:6] + "-" + file_date_str[6:]

# Extract the file date from IMG-########-???.jpg
def GetFileDate_IMG(a_filename):
    parts = a_filename.split('-')
    # There must be at least 3 parts
    if len(parts) < 3:
        return ""
    file_date_str = parts[1]
    if len(file_date_str) != 8:
        return ""
    return file_date_str[:4] + "-" + file_date_str[4:6] + "-" + file_date_str[6:]

def GetFileDate(a_file):
    _, file_name = os.path.split(a_file)
    file_date = ""
    if file_name[:4] == "PXL_":
        file_date = GetFileDate_PXL(file_name)
    elif file_name[:4] == "IMG-":
        file_date = GetFileDate_IMG(file_name)
    return file_date

def ImportPhonePhotos(a_source_dir, a_dest_dir):
    #ClearDir(dest_dir)
    all_files = GetSourceFiles(a_source_dir)
    for src_file_name in all_files:
        src_file_full_name = os.path.join(a_source_dir, src_file_name)

        #
        # The file must pass various checks to be imported.
        #
        file_qualification = QualifyFileSize(src_file_full_name)
        if not file_qualification["qualified"]:
            print(src_file_name, file_qualification["reason"])
            continue

        #
        # Get the file's date. It will be used to name the file's destination folder.
        #
        file_date = GetFileDate(src_file_full_name)
        if file_date == "":
            print(src_file_name, "Error parsing file name")
            continue

        # If the photo's folder does not exist, create it.
        dest_file_path = os.path.join(a_dest_dir, file_date)
        if not os.path.isdir(dest_file_path):
            try:
                os.mkdir(dest_file_path)
            except OSError:
                print(src_file_name, "Error creating directory " + dest_file_path)
                continue
        
        #
        # Copy the file to its destination folder.
        #
        dest_file_full_name = os.path.join(dest_file_path, src_file_name)
        action_string = "copied"
        if os.path.isfile(dest_file_full_name):
            if os.path.getsize(dest_file_full_name) == os.path.getsize(src_file_full_name):
                action_string = "skipped"
            else:
                action_string = "overwritten"
        
        try:
            if action_string != "skipped":
                shutil.copy2(src_file_full_name, dest_file_full_name)
        except Exception as e:
            print(src_file_name, "Error copying file to", dest_file_path, ": " + e.strerror)
            continue

        print("OK:", src_file_name, action_string)

def DisplayHelp():
    help_text = """
Options:
  -h, /h     Show this help message
  -t, /t     Display "test"
  """
    print(help_text)
    
def main():
    args = sys.argv[1:] # Skip script name

    if not args:
        print("No arguments passed.")
        DisplayHelp()
        return
    
    for arg in args:
        if arg in ("-h", "/h"):
            DisplayHelp()
            return
        elif arg in ("-t", "/t"):
            source_dir = default_source_dir
            dest_dir = default_dest_dir
            print(">>> Testing mode ")
            print(f"      From: {source_dir}")
            print(f"        To: {dest_dir}")
            ImportPhonePhotos(source_dir, dest_dir)

if __name__ == "__main__":
    main()
