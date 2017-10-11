import cv2
import logging
from stego import ConcealException

logger = logging.getLogger(__name__)


class Image(object):
    """
    Image Class

    An Image object for holding the Carrier image
    """
    def __init__(self, path):
        """
        Init Function

        :param path:
        """
        self.file_path = path

        self.image = None
        self.height = None
        self.width = None
        self.channels = None

    def read(self, file=None):
        """
        Read Function

        Read in an image into memory
        :param file:
        :return:
        """
        logger.info("Reading carrier file in...")

        try:
            self.image = cv2.imread(file or self.file_path)
            self.height, self.width, self.channels = self.image.shape
            logger.debug("Image has dimensions: {}".format(self.image.shape))

            return True
        except Exception as e:
            ConcealException("Unable to read in carrier image")

        return False

    def write(self, out):
        """
        Write Function

        Write the image to a specified file
        :param out:
        :return:
        """
        cv2.imwrite(out, self.image)
        return
