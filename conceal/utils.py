import logging
import base64

logger = logging.getLogger(__name__)


class ConcealException(Exception):
    pass


class Utils(object):

    @staticmethod
    def check_carrier_image(carrier, file):
        logger.info("Checking carrier image for adequate size...")

        length = len(file)
        if carrier.width * carrier.height * carrier.channels < length + 64:
            raise ConcealException("Carrier image is not large enough")

    @staticmethod
    def binary_value(val, bit_size):
        binary = bin(val)[2:]

        if len(binary) > bit_size:
            raise ConcealException("Binary value is larger than the specified bit size")

        while len(binary) < bit_size:
            binary = "0" + binary

        return binary

    @staticmethod
    def encrypt(key, string):
        logger.info("Preparing to encrypt hidden file...")
        enc = []
        for i in range(len(string)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(string[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc))

    @staticmethod
    def decrypt(key, string):
        logger.info("Preparing to decrypt hidden file...")
        dec = []
        enc = base64.urlsafe_b64decode(string)
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)