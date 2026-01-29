import win32com.client
import time
import os
from typing import Iterable, Callable

class AndroidPhone:
    """
    Properties:
    phone
    __photoFolder
    __connected
    __files
    """
    ###########################
    # Constructor
    def __init__(self):
        self.__connected = False

        # 1. Initialize the Windows Shell Application
        shell = win32com.client.Dispatch("Shell.Application")

        # 2. Access "This PC" (represented by the Shell Constant 17)
        # This is the root where MTP devices (phones) appear
        this_pc = shell.Namespace(17)

        self.phone = None
        # 3. Look for your phone in the list of "This PC" items
        for item in this_pc.Items():
            # Android phones usually appear with their model name
            # We check if it's a folder-like object without a drive letter
            if not os.path.exists(item.Path) and item.IsFolder:
                self.phone = item
                break

        if not self.phone:
            print("Android device not found. Ensure it's in 'File Transfer' mode.")
            return
        
        self.__photoFolder = self.goToPhotoFolder()
        self.__connected = True
        print (f"Phone {self.phone.Name} initialized. At {self.__photoFolder.Title}.")
        self.__files = self.listFileNames()
        print(f"Found {len(self.__files)} files.")

    ###########################
    # Go to photo folder
    def goToPhotoFolder(self):

        # Specify location of camera photos
        target_path = ["Internal shared storage", "DCIM", "Camera"]

        # Start at the phone root
        current_folder = self.phone.GetFolder

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
        return current_folder


    ###########################
    # List files
    def listFileNames(self):
        files = []
        if not self.__connected:
            print("Not connected.")
            return files
        
        extensions = ('.jpg', '.jpeg', '.png', '.mpeg', '.mov')
        for file in self.__photoFolder.Items():
            if file.Name.lower().startswith(".trashed"):
                continue
            if not file.Name.lower().endswith(extensions):
                continue    
            files.append(file.Name)
        return files


    ###########################
    # Get file size
    def getFileSize(self, a_file_name):
        if not self.__connected:
            print("Not connected.")
            return 0
        
        # Find the file in the folder
        file = self.__photoFolder.ParseName(a_file_name)

        # This is more exact than current_folder.GetDetailsOf(file, 2)
        exact_size = file.ExtendedProperty("System.Size")
        file_size = 0
        try:
            file_size = int(exact_size)
        except ValueError:
            file_size = 0

        return file_size


    ###########################
    # Copy file to local folder
    def copyFileToLocal(self, a_file_name, a_dest_path):
        if not self.__connected:
            print("Not connected.")
            return False
        
        # To copy files from an Android device (MTP) to a local folder using win32com, 
        # you must use the Folder.CopyHere() method on the destination folder. 

        # Since Android devices are not assigned drive letters, standard Python libraries 
        # like shutil won't work; you must treat the destination as a Shell namespace.

        # 1. Ensure the destination directory exists
        if not os.path.exists(a_dest_path):
            print(f"Folder '{a_dest_path}' does not exist on local drive.")
            return False
        
        # 2. Get the FolderItem object for the file on the phone
        file_item = self.__photoFolder.ParseName(a_file_name)
        if not file_item:
            print(f"File '{a_file_name}' not found on phone.")
            return False
        
        # 3. Create a Shell folder object for the local destination
        # NOTE: Reusing the same shell as the phone results in an error. Need a new shell.
        shell = win32com.client.Dispatch("Shell.Application")
        dest_folder = shell.NameSpace(os.path.abspath(a_dest_path))

        # 4. Use CopyHere to pull the file from the phone to the PC
        # Options: 
        #    4 = No progress bar
        #    8 = Automatically rename the file if the target name exists (FOF_RENAMEONCOLLISION)
        #   16 = Respond "Yes to All" for dialogs 
        #   64 = Preserve undo information (FOF_ALLOWUNDO)
        #  128 = Perform operation only if a wildcard (*.*) is used (FOF_FILESONLY)
        #  256 = Show progress dialog but hide file names (FOF_SIMPLEPROGRESS)
        #  512 = Do not confirm new directory creation (FOF_NOCONFIRMMKDIR)
        # 1024 = No UI on file copy errors
        # 4096 = Copy only local files in a folder, disabling recursion (FOF_NORECURSION)
        # Constants for readability
        FOF_SILENT = 4
        FOF_NOCONFIRMATION = 16
        FOF_NOERRORUI = 1024
        dest_folder.CopyHere(file_item, FOF_NOERRORUI + FOF_NOCONFIRMATION + FOF_SILENT)

        # 5. Poll for completion.
        # CopyHere() is asynchronous and there is no other way to know
        # when it completed.
        local_file = os.path.join(a_dest_path, a_file_name)
        timeout = 30 # seconds
        start = time.time()
        while time.time() - start < timeout:
            if os.path.exists(local_file):
                return True
            time.sleep(0.1)

        print(f"Error copying file {a_file_name} to {a_dest_path}.")
        return False




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
    p = AndroidPhone()
    file_list = p.listFileNames()
    print(f"{file_list[3]} -- Size={p.getFileSize(file_list[3])}")
    p.copyFileToLocal(file_list[3], r"C:\Users\alex_\Documents\Projects\PhonePhotoImporter\TestSrc")

    # file_list = list_android_photos({display_file_details})
    # print(f"{len(file_list)} files.")

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