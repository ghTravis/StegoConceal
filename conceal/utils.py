import logging
import base64

logger = logging.getLogger(__name__)


class ConcealException(Exception):
    """
    Conceal Exception

    Simple wrapper for throwing Conceal Exceptions
    """
    pass


class Utils(object):
    """
    Utils Class

    Contains helper functions for operating on Images with Steganography
    """

    @staticmethod
    def check_carrier_image(carrier, file):
        """
        Check Carrier Image

        Check the carrier image for proper file length in order to hold the secret file data
        :param carrier:
        :param file:
        :return:
        """
        logger.info("Checking carrier image for adequate size...")

        length = len(file)
        if carrier.width * carrier.height * carrier.channels < length + 64:
            raise ConcealException("Carrier image is not large enough")

    @staticmethod
    def binary_value(val, bit_size):
        """
        Binary Value

        Convert a given value into a binary value of a given bit size
        :param val:
        :param bit_size:
        :return:
        """
        binary = bin(val)[2:]

        if len(binary) > bit_size:
            raise ConcealException("Binary value is larger than the specified bit size")

        while len(binary) < bit_size:
            binary = "0" + binary

        return binary

    @staticmethod
    def encrypt(key, string):
        """
        Encrypt

        Encrypt a string using the Vigenere Cipher, requiring a secret key
        :param key:
        :param string:
        :return:
        """
        logger.info("Preparing to encrypt hidden file...")
        enc = []

        # encode each character of the string with the addition of the ordinal of a specific character of the key
        for i in range(len(string)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(string[i]) + ord(key_c)) % 256)
            enc.append(enc_c)

        # return a url safe base64 encoded version of the encrypted string
        return base64.urlsafe_b64encode("".join(enc))

    @staticmethod
    def decrypt(key, string):
        """
        Decrypt

        Decrypt a string using the Vigenere Cipher, requiring a
        :param key:
        :param string:
        :return:
        """
        logger.info("Preparing to decrypt hidden file...")
        dec = []

        # decode the encrypted string from base64
        enc = base64.urlsafe_b64decode(string)

        # decode each character in the string with the subtraction of the ordinal of a specific character of the key
        # store it as a list of characters
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)

        # convert the list into a string and return it
        return "".join(dec)
