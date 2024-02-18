import subprocess
import shutil
import os
import datetime
import time
import random
import string

def generate_folder(base_path, permission=700):
    """
    Generates a new folder with the specified permissions

    string base_path: parent folder to generate the new folder
    int permission: The permission code for the folder. Default is 700,
        meaning that the folder is accessible by root only
    """
    # Generate folder name
    folder_name = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    folder_path = os.path.join(base_path, folder_name)

    # Re run above code until it is confirmed we have a new folder
    while os.path.isdir(folder_path):
        folder_name = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        unique_random_key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        folder_path = os.path.join(base_path, f"{folder_name}{unique_random_key}")
    
    # generate folder
    os.makedirs(folder_path)
    
    # modify folder settings permissions
    try:
        subprocess.run(["sudo", "chmod", str(permission), folder_path], check=True)
    except Exception as e:
        # Catch for errors, likely from non existing permission code
        print(e)
        os.rmdir(folder_path)
        return None

    return folder_path

def is_expired(path, days_for_expire=0):
    """
    Checks the last time a file or folder has been accessed. If it has not 
    been accessed in the days specified, then return True. False if otherwise.

    string days: The full path to the file that is being checked
    int days: The amount of days since last access that indicates that a file
        has expired. 
    """
    current_time = time.time()

    # get last access time (includes change and modification times)
    file_stat = os.stat(path)
    last_access = file_stat.st_atime

    # Generate amount of time since last access
    seconds_last_access = (current_time - last_access) 

    # compare days for expiry (in seconds) to the time since last access
    return (days_for_expire * 24 * 60 * 60) < seconds_last_access

def get_file_creator(file_path):
    """
    Gets the file creators username

    ls -l filepath command on linux returns something like this:
    -rw-rw-r-- 1 machung machung 4 Feb 17 05:14 /home/machung/test.txt
    So we select the file owner username from this command output. 

    string file_path: The absolute path of the file
    """
    sub_result = subprocess.run(["ls", "-l", file_path], capture_output=True)
    print(sub_result.stderr)
    if not sub_result.stderr:
        file_owner = sub_result.stdout.decode().split()[2]
        return file_owner
    return None

def notify_file_creator(file_creator):
    """
    TODO: implement proper notification system
    """
    print(f"Deleting file by ", file_creator)

def delete_expired_files(folder_path):
    """
    Goes through all files in a folder, and deletes the ones that
    have expired

    string base_folder: The folder containing the files to delete
    """
    if not os.path.isdir(folder_path):
        print("Base folder does not exist")
        return

    temp_folder = generate_folder(os.path.dirname(folder_path))
    if temp_folder is None:
        print("Unable to create a temporary folder, cancelling file deletion")
        return

    with os.scandir(folder_path) as entries:
        for entry in entries:
            if entry.is_file() or entry.is_dir():
                entry_path = os.path.join(folder_path, entry.name)

                entry_path_no_ext, ext = os.path.splitext(entry_path)
                unique_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
                unique_random_key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
                entry_path_unique = f"{entry_path_no_ext}_{unique_timestamp}_{unique_random_key}{ext}"
                
                os.rename(entry_path, entry_path_unique)
                shutil.move(entry_path_unique, temp_folder)
    
    shutil.rmtree(temp_folder)
