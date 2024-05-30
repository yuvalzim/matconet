import os
import socket
import threading
import pickle
import time
from consts import *
import process_check
from Crypto import Random
from encrypt import *
from Crypto.PublicKey import RSA
import filesUtil
import random
import enable_py_privs
import protocol as protocol
import hash_api as hash_api
import folder_scan
import subprocess
import file_content_manipulation
import execute_rtm
import glob


class Server:

    def __init__(self):
        hash_api.download_hash()
        filesUtil.create_quarantine_folder()
        #execute_rtm.execute_rtm_engine()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", PORT_DST))
        self.server_socket.listen()

    def start(self):
        while True:
            self.client_socket, self.clients_address = self.server_socket.accept()
            data = self.client_socket.recv(BUFFER_SIZE).decode()
            if data == "CONNECT":
                session = ClientSession(self.client_socket)
                session.start()


class ClientSession(threading.Thread):
    def __init__(self, client_socket):
        self.commands = {"PROCESS_CHECK": self.handle_process_check, "SELECT_DIR": self.choose_dir,
                         "START_SCAN": self.initiate_scan, "SCAN_DIR": self.scan_dir, "CLOSE_PROC": self.close_proc,
                         "REDUCE_PRIVS": self.reduce_privs, "DELETE_FILE": self.delete_file,
                         "QUARANTINE_FILE": self.quarantine_file, "VIEW_QUARANTINE": self.get_quarantined_files,
                         "RESTORE_FILE": self.restore_file, "DELETE_ALL": self.delete_all_files,
                         "RESTORE_ALL": self.restore_all_files}

        self.client_socket = client_socket
        key = RSA.generate(1024)
        self.private_key = key.exportKey()
        self.public_key = key.publickey().exportKey()
        self.current_path = ""
        threading.Thread.__init__(self)

    def run(self):
        # send public key
        self.client_socket.send(self.public_key)
        # recv client key
        data = self.client_socket.recv(BUFFER_SIZE)
        self.decryptor = PKCS1_OAEP.new(RSA.importKey(self.private_key))
        self.key = self.decryptor.decrypt(data)
        self.obj = Encrypt(self.key)
        self.send_ack()
        while True:
            try:
                operation = protocol.get_data(self.client_socket)
            except ConnectionResetError as e:
                print(e)
                break
            operation = self.obj.decryption(operation).decode()
            operation = operation.split(" ")
            if len(operation) > 1:
                self.arg = " ".join(operation[1:])
            if operation[0] == "BACK":
                continue
            if operation[0] not in self.commands.keys():
                continue
            self.commands[operation[0]]()

    def send_ack(self):
        self.client_socket.send("ack".encode())

    def handle_process_check(self):
        proc_dict = process_check.get_proc_dict()
        dict_bytes = pickle.dumps(proc_dict)
        print(dict_bytes)
        self.client_socket.send(self.obj.encryption(dict_bytes))

    def close_proc(self):
        pid = int(self.arg)
        process_check.close_proc(pid)

    def reduce_privs(self):
        pid = int(self.arg)
        process_check.disable_privs(pid)

    def initiate_scan(self):
        self.current_path = ""
        disc_names = filesUtil.get_disk_names()
        disc_names_bytes = pickle.dumps(disc_names)
        encrypted_names = self.obj.encryption(disc_names_bytes)
        self.client_socket.send(encrypted_names)

    def choose_dir(self):
        dir_name = self.arg
        if not os.path.isdir(self.current_path + dir_name):
            self.scan_dir()
            return
        dir_name = self.arg
        if self.current_path:
            self.current_path += f"{dir_name}\\"
        else:
            self.current_path += dir_name
        content = os.listdir(self.current_path)
        pickled_content = pickle.dumps(content)
        encrypted_content = self.obj.encryption(pickled_content)
        protocol.send_data(self.client_socket, encrypted_content)

    def scan_dir(self):
        protocol.send_data(self.client_socket, self.obj.encryption(pickle.dumps("START_SCAN")))
        data = self.obj.decryption(protocol.get_data(self.client_socket)).decode().split(" ")
        is_sub = False
        print(data)
        if data[0] == "BACK":
            return
        if len(data) > 1:
            is_sub = True
        path = self.current_path + data[0]
        hash_download_thread = threading.Thread(target=hash_api.download_hash())
        hash_download_thread.start()
        if os.path.isfile(path):
            files_list = [path]
        else:
            if is_sub:
                files_list = folder_scan.list_files_sub(path)
            else:
                files_list = folder_scan.list_files(path)
        hash_download_thread.join()
        for i in folder_scan.scan(files_list):
            protocol.send_data(self.client_socket, self.obj.encryption(i))

    def delete_file(self):
        filesUtil.delete_file(self.arg)

    def quarantine_file(self):
        file_content_manipulation.move_to_quarantine(self.arg)

    def get_quarantined_files(self):
        files_list = filesUtil.get_quarantined_files()
        files_list_pickled = pickle.dumps(files_list)
        protocol.send_data(self.client_socket, self.obj.encryption(files_list_pickled))

    def restore_file(self):
        file_content_manipulation.restore_file(self.arg)

    def delete_all_files(self):
        path = os.path.dirname(__file__)
        full_path = os.path.join(path, QUARANTINE_PATH)
        files = glob.glob(full_path + "/*")
        for file in files:
            os.remove(file)


    def restore_all_files(self):
        path = os.path.dirname(__file__)
        full_path = os.path.join(path, QUARANTINE_PATH)
        files_list = folder_scan.list_files(full_path)
        for file in files_list:
            file_content_manipulation.restore_file(os.path.basename(file))

def main():
    enable_py_privs.enable_privs()
    server = Server()
    server.start()


if __name__ == '__main__':
    main()
