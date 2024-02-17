import subprocess
import shutil
import os
import datetime
import time

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
        folder_path = os.path.join(base_path, folder_name)
    
    # generate folder
    os.makedirs(folder_path)
    
    # modify folder settings permissions
    try:
        subprocess.run(["sudo", "chmod", str(permission), folder_path], check=True)
    except subprocess.CalledProcessError as e:
        # Catch for errors, likely from non existing permission code
        print(e.stderr.decode(encoding='utf-8').strip())
        os.rmdir(folder_path)
        return None

    return folder_path

def is_expired_file(file_path, days_for_expire):
    """
    Checks the last time a file has been accessed. If it has not been accessed 
    in the days specified, then return True. False if otherwise.

    string days: The full path to the file that is being checked
    int days: The amount of days since last access that indicates that a file
        has expired. 
    """
    current_time = time.time()

    # get last access time (includes change and modification times)
    file_stat = os.stat(file_path)
    last_access = file_stat.st_atime

    # Generate amount of time since last access
    days_last_access = (current_time - last_access) 

    # compare days for expiry (in seconds) to the time since last access
    return (days_for_expire * 24 * 60 * 60) > days_last_access


