from Crypto.Cipher import AES, PKCS1_OAEP
from consts import *
from Crypto.PublicKey import RSA


class Encrypt:

    def __init__(self, key):
        self.__key = key
        self.__obj = AES.new(key, AES.MODE_ECB)

    def __add_padding(self, data):
        """
        Adds padding to the data before encrypting
        :param data: data to encrypt
        :return: data after adding the padding
        """
        count_pad = BLOCK_SIZE - len(data) % BLOCK_SIZE
        if count_pad == BLOCK_SIZE:
            count_pad = 0
        if type(data) is bytes:
            return data + PAD * count_pad
        return data.encode() + PAD * count_pad

    # Strip your data after decryption (with pad and interrupt_
    def __strip_padding(self, data):
        """
        Strips padding off data after decryption
        :param data: decrypted data
        :return: same data without the padding
        """
        return data.rstrip(PAD)

    def encryption(self, src_data):
        """
        Encrypts the given data
        :param src_data:
        :return:
        """
        return self.__obj.encrypt(self.__add_padding(src_data))

    def decryption(self, enc_data):
        """
        Decrypts the data
        :param enc_data: encrypted data
        :return: original data
        """
        data_after_dec = self.__obj.decrypt(enc_data)
        return self.__strip_padding(data_after_dec)
