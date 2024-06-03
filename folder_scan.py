from consts import *
from enable_py_privs import *
import os
import pickle
import threading
import hash_api as hash_api


def list_files_sub(directory: str) -> list[str]:
    """

    :param directory: directory name
    :return: list of files in this directory and it's sub directories
    """
    enable_privs()
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def list_files(directory: str) -> list[str]:
    """
    :param directory: directory name
    :return: list of files in that directory
    """
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def scan(files: list[str]) -> list[str] and bytes:
    """
    :param files: a list of files to scan
    :return: yields which percent of the files were scanned. At the end yields the suspected files
    """
    enable_privs()  # enables privileges for scanning protected files
    with open(HASHES_FILE_NAME, 'r') as hashes_file:
        content = hashes_file.read().split('\n')
    content_set = set(content)
    corrupted_files = []
    num_of_files = len(files)
    count = 0
    complete = 0

    for i in files:
        file_hash = hash_api.calculate_hash(i)
        if file_hash in content_set and file_hash != MD5_NULL_HASH:
            corrupted_files.append(i)
        count += 1
        new_progress = str(round((count / num_of_files) * 100))
        if new_progress != complete:
            complete = new_progress
            yield pickle.dumps(str(round((count / num_of_files) * 100)))

    corrupted_files_bytes = pickle.dumps(corrupted_files)
    yield corrupted_files_bytes





