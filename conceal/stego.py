import logging
import sys
from utils import Utils, ConcealException

logger = logging.getLogger(__name__)


class Stego(object):
    """
    Stego Class

    Perform basic steganography functions on a carrier image and a secret file
    """

    def __init__(self, carrier=None, hide_file=None):
        """
        Init Function

        :param carrier:
        :param hide_file:
        """
        self.carrier = carrier
        self.hide_file = hide_file
        self.output = None

        # keep a list of all of the one positions for masking [00000001, 00000010, 00000100, 00001000, ...]
        self.decimal_mask_one = [1, 2, 4, 8, 16, 32, 64, 128]
        self.mask_one = self.decimal_mask_one.pop(0)

        # keep a list of all of the zero positions for masking [11111110, 11111101, 11111011, 11110111, ...]
        self.decimal_mask_zero = [254, 253, 251, 247, 239, 223, 191, 127]
        self.mask_zero = self.decimal_mask_zero.pop(0)

        # record current values as we shift the bits
        self.cur_height = 0
        self.cur_width = 0
        self.cur_channel = 0

    def encode(self, encrypt=False, mime=None):
        """
        Encode Function

        Encode a secret file into a carrier image
        :param encrypt:
        :param mime:
        :return:
        """
        logger.info("Running encoder...")

        # check carrier image is large enough to hold the secret file
        Utils.check_carrier_image(self.carrier, self.hide_file)

        # encrypt the secret file if specified
        if encrypt:
            self.hide_file = Utils.encrypt(encrypt, self.hide_file)

        # do some light filetype checking on the secret file so we know how to embed it
        if any(x.lower() in str(mime[0]).lower() for x in ['Text', 'None']):
            logger.info("Doing a TEXT encode...")
            self._encode_text()
        elif any(x.lower() in str(mime[0]).lower() for x in ['Application', 'Binary']):
            logger.info("Doing a BINARY encode...")
            self._encode_binary()
        else:
            ConcealException("Unable to read hidden file type")
            logger.fatal("File type {}. Did nothing, exiting.".format(mime))
            sys.exit()

        return self.carrier

    def decode(self, decrypt=False, mime=None):
        """
        Decode Function

        Decode a carrier image to reveal a secret file embedded within
        :param decrypt:
        :param mime:
        :return:
        """
        logger.info("Running decoder...")

        # do some light filetype checking on the secret file so we know how to read it out
        if any(x.lower() in str(mime[0]).lower() for x in ['Text', 'None']):
            logger.info("Doing a TEXT decode...")
            self._decode_text()
        elif any(x.lower() in str(mime[0]).lower() for x in ['Application', 'Binary']):
            logger.info("Doing a BINARY decode...")
            self._decode_binary()
        else:
            ConcealException("Unable to read output file type")
            logger.fatal("File type {}. Did nothing, exiting.".format(mime))
            sys.exit()

        # if the user specifies a password, attempt to decrypt the secret file
        if decrypt:
            self.output = Utils.decrypt(decrypt, self.output)

        return self.output

    def _encode_text(self):
        """
        Encode Text Function
        :return:
        """

        # get length of hidden file
        length = len(self.hide_file)
        logger.debug("Length of hidden file is: {}".format(length))

        # calculate length of hidden file in binary to determine maximum bytes we can store
        # embed the length on the first 4 bytes
        self._embed_binary_val(Utils.binary_value(length, 16))

        # embed all the other bytes (8 bits each)
        for char in self.hide_file:
            c = ord(char)
            self._embed_binary_val(Utils.binary_value(c, 8))

    def _encode_binary(self):
        """
        Encode Binary Function
        :return:
        """

        # get length of hidden file
        length = len(self.hide_file)
        logger.debug("Length of hidden file is: {}".format(length))

        # calculate length of hidden file in binary to determine maximum bytes we can store
        # embed the length on the first 64 bits
        self._embed_binary_val(Utils.binary_value(length, 64))

        # embed all the other bytes, taking special care for special characters commonly found in binary files
        for byte in self.hide_file:
            byte = byte if isinstance(byte, int) else ord(byte)
            self._embed_binary_val(Utils.binary_value(byte, 8))

    def _decode_text(self):
        """
        Decode Text Function
        :return:
        """

        # read in 2 bytes of the carrier image to get the length of the embedded text
        length = int(self._read_bits(16), 2)
        logger.debug("Length of hidden file is: {}".format(length))

        i = 0
        hidden_file = ""

        # read in all embedded bits one at a time and concatenate them together
        while i < length:
            tmp = self._read_bits(8)
            i += 1
            hidden_file += chr(int(tmp, 2))

        self.output = hidden_file

    def _decode_binary(self):
        """
        Decode Binary Function
        :return:
        """

        # read in 8 bytes of the carrier image to get the length of the embedded binary file
        length = int(self._read_bits(64), 2)
        logger.debug("Length of hidden file is: {}".format(length))

        output = b''

        # read in all embedded bits one at a time and concatenate them together
        for i in range(length):

            output += str(int(self._read_bits(8), 2)).encode("utf-8")
        self.output = output

    def _embed_binary_val(self, bits):
        """
        Embed Binary Val Function

        Embed the binary value of the encoded char at a specified pixel coordinate
        :param bits:
        :return:
        """
        logger.debug("Processing bit: {}".format(bits))

        # embed every bit at a different pixel by shifting the least significant bit
        for c in bits:
            # translate the pixel value into a list
            val = list(self.carrier.image[self.cur_height, self.cur_width])
            if int(c) == 1:
                # perform an OR operator on the new pixel value if the bit is a 1
                val[self.cur_channel] = int(val[self.cur_channel]) | self.mask_one
            else:
                # perform an AND operator on the new pixel value if the bit is not a 1
                val[self.cur_channel] = int(val[self.cur_channel]) & self.mask_zero

            logger.debug("Altering pixel {},{},{} with {}".format(self.cur_height, self.cur_width, self.cur_channel, tuple(val)))

            # write the value to the image
            self.carrier.image[self.cur_height, self.cur_width] = tuple(val)
            self._next_slot()

    def _next_slot(self):
        """
        Next Slot Function

        Iterate through the image and determine the next pixel coordinate to bit manipulate
        :return:
        """

        # increment the channel pointer if we're at the end of the channel column
        # increment the width pointer if we're not at the end of the row
        # increment the height pointer if we're at the end of the row
        if self.cur_channel == self.carrier.channels - 1:
            self.cur_channel = 0
            if self.cur_width == self.carrier.width - 1:
                self.cur_width = 0
                if self.cur_height == self.carrier.height - 1:
                    self.cur_height = 0

                    # fail if we've exceeded the maximum bit mask value, otherwise do the next mask value
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

    def _read_bits(self, nb):
        """
        Read Bits Function

        Read the given number of bits
        :param nb:
        :return:
        """

        # read the given bits into a string
        bits = ""
        for i in range(nb):
            val = self.carrier.image[self.cur_height, self.cur_width][self.cur_channel]
            val = int(val) & self.mask_one
            # traverse the bit array
            self._next_slot()
            if val > 0:
                bits += "1"
            else:
                bits += "0"
        logger.info("Binary of hidden byte at {},{},{} is {}".format(self.cur_height, self.cur_width, self.cur_channel, bits))
        return bits
