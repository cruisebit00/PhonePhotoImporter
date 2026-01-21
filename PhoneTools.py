import win32com.client
import os
from typing import Iterable, Callable

def list_android_photos(functions: Iterable[Callable[[str, int], None]]):
    print("Listing photos")
    # 1. Initialize the Windows Shell Application
    shell = win32com.client.Dispatch("Shell.Application")

    # 2. Access "This PC" (represented by the Shell Constant 17)
    # This is the root where MTP devices (phones) appear
    this_pc = shell.Namespace(17)

    phone = None
    # 3. Look for your phone in the list of "This PC" items
    for item in this_pc.Items():
        # Android phones usually appear with their model name
        # We check if it's a folder-like object without a drive letter
        if not os.path.exists(item.Path) and item.IsFolder:
            phone = item
            break

    if not phone:
        print("Android device not found. Ensure it's in 'File Transfer' mode.")
        return
    
    # Image extensions to search for
    target_path = ["Internal shared storage", "DCIM", "Camera"]
    files = []

    # Start at the phone root
    current_folder = phone.GetFolder

    # Navigate through the subfolders
    for folder_name in target_path:
        found = False
        for item in current_folder.Items():
            if item.Name.lower() == folder_name.lower():
                current_folder = item.GetFolder
                found = True
                break
        if not found:
            print(f"Could not find folder: {folder_name}")
            return

    # 4. Run the input funciton on the photo files
    print(f"\nListing photos in {phone.Name}\\{'\\'.join(target_path)}:")
    extensions = ('.jpg', '.jpeg', '.png', '.mpeg', '.mov')
    for file in current_folder.Items():
        if file.Name.lower().startswith(".trashed"):
            continue
        if not file.Name.lower().endswith(extensions):
            continue

        # This is more exact than current_folder.GetDetailsOf(file, 2)
        exact_size = file.ExtendedProperty("System.Size")
        file_size = 0
        try:
            file_size = int(exact_size)
        except ValueError:
            file_size = 0
        
        files.append({"name": file.Name, "size": file_size})

        for func in functions:
            func(file.Name, file_size)
    
    return files


def display_file_details(a_name, a_size):
    print(f"{a_name}: {a_size}")

if __name__ == "__main__":
    file_list = list_android_photos({display_file_details})

    print(f"{len(file_list)} files.")

# """
# From: https://gemini.google.com/app/92219b4d92bea73f

# Prompt to gemini.google.com:

# Write a python function that lists all the photo files on my android phone, in the DCIM\Camera folder. 
# The function should run on Windows. Assume the phone is connected via USB and is in file transfer mode. 
# Do not propose an ADB-based solution. 
# Explain how to install all the necessary python packages, list and document the code.


# To list files on an Android device from Windows **without using ADB**, we must interact with the **Media Transfer Protocol (MTP)**.

# Since Windows does not assign a drive letter (like `C:` or `D:`) to MTP devices, standard Python functions like `os.listdir()` will not work. Instead, we use the **Windows Shell COM API** to browse the "Virtual Folders" you see in File Explorer.

# ### 1. Installation

# You will need the `pywin32` package, which allows Python to communicate with the Windows COM objects that manage the shell namespace.

# Open your terminal or command prompt and run:

# ```bash
# pip install pywin32

# ```

# ---

# ### 2. The Python Code

# This script navigates the Windows Shell Namespace to find your phone, enter its storage, and recursively find image files.

# ```python
# import win32com.client
# import os

# def list_phone_photos():
#     # 1. Access the Windows Shell Application
#     shell = win32com.client.Dispatch("Shell.Application")
    
#     # 2. Namespace(17) is the virtual folder for "This PC"
#     this_pc = shell.Namespace(17)
    
#     phone = None
#     # Look for the phone among devices in "This PC"
#     for item in this_pc.Items():
#         # Android devices usually show up by their Model Name
#         # We check for a folder-like item that doesn't have a drive letter
#         if item.IsFolder and not os.path.exists(item.Path):
#             phone = item
#             break
            
#     if not phone:
#         print("Error: Android phone not found. Is it connected and in 'File Transfer' mode?")
#         return

#     print(f"Connected to: {phone.Name}")

#     # 3. Define the path we want to reach
#     # Note: On some phones, 'Internal shared storage' might be 'Phone' or 'Internal Storage'
#     target_path = ["Internal shared storage", "DCIM", "Camera"]
    
#     # Start at the phone root
#     current_folder = phone.GetFolder
    
#     # Navigate through the subfolders
#     for folder_name in target_path:
#         found = False
#         for item in current_folder.Items():
#             if item.Name.lower() == folder_name.lower():
#                 current_folder = item.GetFolder
#                 found = True
#                 break
#         if not found:
#             print(f"Could not find folder: {folder_name}")
#             return

#     # 4. List the photo files
#     print(f"\nListing photos in {phone.Name}\\{'\\'.join(target_path)}:")
#     extensions = ('.jpg', '.jpeg', '.png', '.webp', '.heic')
    
#     count = 0
#     for file in current_folder.Items():
#         if file.Name.lower().endswith(extensions):
#             print(f" - {file.Name}")
#             count += 1
            
#     if count == 0:
#         print("No photos found in the Camera folder.")
#     else:
#         print(f"\nTotal: {count} photos found.")

# if __name__ == "__main__":
#     list_phone_photos()
# ```

# ---

# ### 3. How it Works

# * **`Shell.Application`**: This is the same engine Windows Explorer uses. It doesn't care about drive letters; it treats the phone as a "Namespace" item.
# * **Virtual Paths**: Because there is no drive letter, the `item.Path` will look like a long string of hardware IDs (e.g., `::{20D0...}\\\?\usb#vid...`). This is normal for MTP.
# * **Recursive Crawling**: The `crawl_folder` function treats the phone's "Internal Storage" just like a folder tree, moving from the root into directories like `DCIM` and `Pictures`.

# ### Important Notes

# * **Unlock the Phone**: If your phone screen is locked, Windows will see the device but show it as empty for security reasons.
# * **Performance**: MTP is significantly slower than a hard drive. If you have thousands of photos, the script may take a minute or two to finish listing them.

# **Would you like me to show you how to filter the search specifically to the "DCIM/Camera" folder to make it run faster?**
# """