import logging

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
