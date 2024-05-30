from consts import *
import os


def get_file_content(file_path: str) -> bytes:
    with open(file_path, 'rb') as file:
        contents = file.read()
    os.remove(file_path)
    return contents


def create_new_file(file_path: str, content: bytes) -> None:
    file_name = os.path.basename(file_path)
    new_file_path = f"{QUARANTINE_PATH}\\{file_name}"
    with open(new_file_path, 'ab') as new_file:
        old_path_bytes = file_path.encode()
        new_file.write(old_path_bytes + b"\n" + content)


def move_to_quarantine(file_path: str):
    file_content = get_file_content(file_path)
    create_new_file(file_path, file_content)


def restore_file(file_name: str):
    file_path = f"{QUARANTINE_PATH}\\{file_name}"
    with open(f"{QUARANTINE_PATH}\\{file_name}", 'rb') as file:
        old_file_path = file.readline().decode().rstrip()
        file_content = file.read()
    os.remove(file_path)

    with open(f"{old_file_path}", 'ab') as new_file:
        new_file.write(file_content)


