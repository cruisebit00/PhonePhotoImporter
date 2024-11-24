import os
import shutil

# Importer parameters
source_dir = "TestSrc"
dest_dir = "TestDest"

def ClearDir(a_dir):
    if a_dir != dest_dir:
        print("Not clearing non-test dir", a_dir)
        return
    try:
        files = os.listdir(a_dir)
        for file in files:
            file_path = os.path.join(a_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("Destination dir", a_dir, "cleared.")
    except OSError:
        print("Error occured clearing dir", a_dir)

def GetSourceFiles(a_source_dir):
    return os.listdir(a_source_dir)

def QualifyFile(a_file):

    # File too small
    size_threshold = 600*1024
    if os.path.getsize(a_file) < size_threshold:
         return {"qualified": False, "reason": "Size under threshold " + f"{size_threshold:,}"}
    
    return {"qualified": True, "reason": ""}

def GetFileDate(a_file):
    _, file_name = os.path.split(a_file)
    parts = file_name.split('_')
    # There must be at least 3 parts
    if len(parts) < 3:
        return ""
    file_date_str = parts[1]
    if len(file_date_str) != 8:
        return ""
    return file_date_str[:4] + "-" + file_date_str[4:6] + "-" + file_date_str[6:]

#ClearDir(dest_dir)
all_files = GetSourceFiles(source_dir)
for src_file_name in all_files:
    src_file_full_name = os.path.join(source_dir, src_file_name)

    #
    # The file must pass various checks to be imported.
    #
    file_qualification = QualifyFile(src_file_full_name)
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
    dest_file_path = os.path.join(dest_dir, file_date)
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
        action_string = "overwritten"
    
    try:
        shutil.copy2(src_file_full_name, dest_file_full_name)
    except Exception as e:
        print(src_file_name, "Error copying file to", dest_file_path, ": " + e.strerror)
        continue

    print("OK:", src_file_name, action_string)
