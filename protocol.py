from consts import *


def send_data(socket, msg):
    data_len = str(len(msg)).zfill(LENGTH_FIELD_SIZE)
    socket.send(data_len.encode())
    socket.send(msg)


def get_data(socket):
    data_length = int(socket.recv(LENGTH_FIELD_SIZE).decode())
    data = socket.recv(data_length)
    return data
