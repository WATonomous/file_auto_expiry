import os
import pwd
from ..data.tuples import *

def get_file_creator(path):
    """
    Returns a tuple including the file creator username, 
    their UID, and GID in that order respectively. 

    string file_path: The absolute path of the file
    """
    # Get the UID of the file or directory owner
    # Get the username associated with the UID
    try:
        username = pwd.getpwuid(os.stat(path).st_uid).pw_name
    except KeyError:
        """ FIX THIS LATER"""
        return f"user{os.stat(path).st_uid}"
    return creator_tuple(username, os.stat(path).st_uid, os.stat(path).st_gid)
