import logging
import sys
from utils import Utils

logger = logging.getLogger(__name__)


class ConcealException(Exception):
    """
    Exception class for handling errors
    """
    pass


class Stego(object):
    def __init__(self, carrier=None, hide_file=None):
        self.carrier = carrier
        self.hide_file = hide_file
        self.output = None

        # calculate all of the zero positions [00000001, 00000010, 00000100, 00001000, ...]
        self.decimal_mask_one = [1, 2, 4, 8, 16, 32, 64, 128]
        self.mask_one = self.decimal_mask_one.pop(0)

        # calculate all of the zero positions [11111110, 11111101, 11111011, 11110111, ...]
        self.decimal_mask_zero = [254, 253, 251, 247, 239, 223, 191, 127]
        self.mask_zero = self.decimal_mask_zero.pop(0)

        # record current values as we shift the bits
        self.cur_height = 0
        self.cur_width = 0
        self.cur_channel = 0

    def encode(self, encrypt=False, mime=None):
        logger.info("Running encoder...")

        Utils.check_carrier_image(self.carrier, self.hide_file)

        if any(x.lower() in str(mime[0]).lower() for x in ['Text', 'None']):
            logger.info("Doing a TEXT encode...")
            self.encode_text()
        elif "binary" in mime:
            logger.info("Doing a BINARY encode...")
            self.encode_binary()
        else:
            ConcealException("Unable to read hidden file type")
            logger.fatal("File type {}. Did nothing, exiting.".format(mime))
            sys.exit()

        return self.carrier

    def decode(self, mime):
        logger.info("Running decoder...")
        if any(x.lower() in str(mime[0]).lower() for x in ['Text', 'None']):
            logger.info("Doing a TEXT decode...")
            self.decode_text()
        elif "binary" in mime:
            logger.info("Doing a BINARY decode...")
            self.decode_binary()
        else:
            ConcealException("Unable to read output file type")
            logger.fatal("File type {}. Did nothing, exiting.".format(mime))
            sys.exit()

        return self.output

    def encode_text(self):
        l = len(self.hide_file)
        logger.debug("Length of hidden file is: {}".format(l))

        binl = Utils.binary_value(l, 16)  # Length coded on 2 bytes so the text size can be up to 65536 bytes long
        logger.debug(binl)

        self.put_binary_value(binl)  # Put text length coded on 4 bytes
        for char in self.hide_file:  # And put all the chars
            c = ord(char)
            self.put_binary_value(Utils.binary_value(c, 8))

    def encode_binary(self):
        l = len(self.hide_file)
        logger.debug("Length of hidden file is: {}".format(l))

        self.put_binary_value(Utils.binary_value(l, 64))
        for byte in self.hide_file:
            byte = byte if isinstance(byte, int) else ord(byte)  # Compat py2/py3
            self.put_binary_value(Utils.binary_value(byte, 8))

    def decode_text(self):
        ls = self.read_bits(16)  # Read the text size in bytes
        l = int(ls, 2)
        i = 0
        unhideTxt = ""
        while i < l:  # Read all bytes of the text
            tmp = self.read_bits(8)  # So one byte
            i += 1
            unhideTxt += chr(int(tmp, 2))  # Every chars concatenated to str
        self.output = unhideTxt

    def decode_binary(self):
        l = int(self.read_bits(64), 2)
        output = b""
        for i in range(l):
            output += chr(int(self.read_bits(8), 2)).encode("utf-8")
        self.output = output

    def put_binary_value(self, bits):  # Put the bits in the image
        logger.debug("Processing bit: {}".format(bits))
        for c in bits:
            val = list(self.carrier.image[self.cur_height, self.cur_width])  # Get the pixel value as a list
            logger.debug("Altering pixel at coordinates: {}".format(val))
            if int(c) == 1:
                val[self.cur_channel] = int(val[self.cur_channel]) | self.mask_one  # OR with maskONE
            else:
                val[self.cur_channel] = int(val[self.cur_channel]) & self.mask_zero  # AND with maskZERO

            logger.debug("Altering pixel {},{} with {}".format(self.cur_height, self.cur_width, tuple(val)))
            self.carrier.image[self.cur_height, self.cur_width] = tuple(val)
            self.next_slot()

    def next_slot(self):  # Move to the next slot were information can be taken or put
        logger.debug("Before: {},{},{}".format(self.cur_height, self.cur_width, self.cur_channel))
        if self.cur_channel == self.carrier.channels - 1:  # Next Space is the following channel
            self.cur_channel = 0
            if self.cur_width == self.carrier.width - 1:  # Or the first channel of the next pixel of the same line
                self.cur_width = 0
                if self.cur_height == self.carrier.height - 1:  # Or the first channel of the first pixel of the next line
                    self.cur_height = 0
                    if self.mask_one == 128:  # Mask 1000000, so the last mask
                        raise ConcealException("No available slot remaining (image filled)")
                    else:  # Or instead of using the first bit start using the second and so on..
                        self.mask_one = self.decimal_mask_one.pop(0)
                        self.mask_zero = self.decimal_mask_zero.pop(0)
                else:
                    self.cur_height += 1
            else:
                self.cur_width += 1
        else:
            self.cur_channel += 1

        logger.debug("After: {},{},{}".format(self.cur_height, self.cur_width, self.cur_channel))

    def read_bits(self, nb):  # Read the given number of bits
        bits = ""
        for i in range(nb):
            bits += self.read_bit()
        return bits

    def read_bit(self):
        val = self.carrier.image[self.cur_height, self.cur_width][self.cur_channel]
        val = int(val) & self.mask_one
        self.next_slot()
        if val > 0:
            return "1"
        else:
            return "0"