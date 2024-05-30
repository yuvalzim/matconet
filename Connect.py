import SendArp
import socket
from consts import *
import threading


class Connection(threading.Thread):
    def __init__(self, ip):
        super().__init__()
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__ip = ip
        self.__status = False  # True - server running. False - server not running

    def run(self):
        """
        Tries to connect to the server
        """
        self.__sock.settimeout(1)
        try:
            self.__sock.connect((self.__ip, PORT_DST))
            self.__sock.send("TEST".encode())
            self.__status = True
        except socket.timeout as err:
            pass
        finally:
            self.__sock.close()

    def get_status(self):
        """
        :return: status of the connection
        """
        return self.__status

    def getip(self):
        """
        :return: Ip of the server
        """
        return self.__ip


def get_successful_cons():
    """

    :return: dictionary containing {Ip: mac_address}
    """
    addresses = SendArp.get_addresses_dict()
    successful_cons = {}
    thread_list = []

    for ip in addresses.keys():
        con = Connection(ip)
        con.start()
        thread_list.append(con)
    for i in thread_list:
        i.join()
        if i.get_status():
            successful_cons[i.getip()] = addresses.get(i.getip())
    return successful_cons


