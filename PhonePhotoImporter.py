import os
import re
import shutil
import sys

# Supporting libraries
#from PIL import Image

# Importer parameters
from defaults import *
from utils import *
from PhoneTools import AndroidPhone


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

#######################################
#
# This function is the main coordinator of the workflow.
#
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

#######################################
#
# Copy photos from the phone to the stage folder
#
def CopyPhotosFromPhone(a_dest_folder):
    num_skipped_files = 0;
    num_copied_files = 0;
    num_errors = 0;
    phone = AndroidPhone()
    file_list = phone.listFileNames()
    for file_name in file_list:
        # If the file already exists in the staging folder, skip the copy.
        if os.path.exists(os.path.join(a_dest_folder, file_name)):
            num_skipped_files += 1
            continue

        # Copy the file
        success = phone.copyFileToLocal(file_name, a_dest_folder)
        num_copied_files += success # Increment copied files if success
        num_errors += not success   # Increment the number of errors if not success

    print(f"Copied: {num_copied_files}    Skipped: {num_skipped_files}    Errors: {num_errors}")



#######################################
#
# Find latest photo
#
def FindLatestPhoto(a_dir, must_have_underscore=True):
    # 1. Find the folder with the latest date
    # Pattern: yyyy-mm-dd_ (or yyyy-mm-dd if must_have_underscore is False)
    latest_folder = None
    latest_folder_date = ""
    
    if not os.path.exists(a_dir):
        return None

    # If underscores are on, look only for names ending with _.
    # If underscores are off, look for all names, either ending or not ending with an underscore.
    pattern_core = r"^(\d{4})-(\d{2})-(\d{2})"
    pattern = f"{pattern_core}{'_' if must_have_underscore else '_?'}$"

    for item in os.listdir(a_dir):
        if os.path.isdir(os.path.join(a_dir, item)):
            # Check if folder matches pattern
            match = re.match(pattern, item)
            if match:
                folder_date = "".join(match.groups())
                if folder_date > latest_folder_date:
                    latest_folder_date = folder_date
                    latest_folder = item

    return latest_folder_date



#######################################
#
# Display usage instructions
#
def DisplayHelp():
    help_text = """
Usage: python PhonePhotoImporter.py [action] [options]

Actions:
  copy       Copy photos from the phone to the staging folder
  import     Sort photos from the staging folder into the destination

Options:
  -h, /h     Show this help message
  -t, /t     Run in test mode
  """
    print(help_text)
    
def main():
    stage_dir = default_stage_dir
    dest_dir = default_destination_dir
    
    # Initialize variables to track user choice
    action = None
    is_test = False

    # Process arguments
    args = sys.argv[1:]
    
    if not args:
        DisplayHelp()
        return    

    for arg in args:
        if arg in ("-h", "/h"):
            DisplayHelp()
            return
        elif arg in ("-t", "/t"):
            is_test = True
            dest_dir = default_test_dir
        elif arg.lower() == "copy":
            action = "copy"
        elif arg.lower() == "import":
            action = "import"
        else:
            print(f"Unrecognized argument: {arg}")
            return
        
    if not action:
        print("Error: You must specify an action ('copy' or 'import').")
        return
    
    if is_test:
        print(">>> Testing mode active")
    elif action == "import":
        input(f"Importing to {dest_dir}. Press ENTER to continue, ^C to abort.")

    print(f"     Stage: {stage_dir}")
    print(f"      Dest: {dest_dir}")

    # Execute based on choice
    if action == "copy":
        print(f"Copying from phone to: {stage_dir}")
        CopyPhotosFromPhone(stage_dir)
    elif action == "import":
        print(f"Importing from {stage_dir} to: {dest_dir}")
        lf = FindLatestPhoto(dest_dir, must_have_underscore=True)
        print(lf)
        #ImportPhonePhotos(stage_dir, dest_dir)


if __name__ == "__main__":
    main()
