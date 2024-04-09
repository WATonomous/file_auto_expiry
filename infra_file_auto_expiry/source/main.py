from utils import *
import time
import typer

app = typer.Typer()

@app.command()
def collect_file_info(path: str, days_for_expire: int = 20):
    current_time = time.time()
    seconds_for_expiry = int(days_for_expire) * 3600 * 24
    collect_expired_file_information(path, current_time, seconds_for_expiry)

@app.command()
def collect_creator_info(path:str, days_for_expire: int=20, replace_file_info: bool=False):
    current_time = time.time()
    seconds_for_expiry = int(days_for_expire) * 3600 * 24
    print(str(replace_file_info))
    collect_creator_information(path, current_time, seconds_for_expiry, replace_file_info)


if __name__ == "__main__":
    app()
