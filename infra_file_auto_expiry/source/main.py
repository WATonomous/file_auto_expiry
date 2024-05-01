from utils import *
import time
import typer
import datetime
app = typer.Typer()

@app.command()
def collect_file_info(path: str, save_file: str = "", days_for_expire: int = 10):
    """
    Collects information about the top level paths within a given folder path
    And dumps it into a json file, specified by the save_file flag
    """
    current_time = time.time()
    seconds_for_expire = int(days_for_expire) * 3600 * 24
    collect_expired_file_information(path, save_file, current_time, seconds_for_expire)
    print(save_file)

@app.command()
def collect_creator_info(file_info: str, save_file: str = ""):
    """
    Tabulates the paths that relate to specific users, based on a given jsonl path
    That jsonl path should be the result of calling the collect_file_info function
    It then dumps the new information into another json file, specified by the save_file flag
    """
    current_time = time.time()
    collect_creator_information(file_info, save_file, current_time)

if __name__ == "__main__":
    app()
