import cv2
import logging
from stego import ConcealException

logger = logging.getLogger(__name__)


class Image(object):
    def __init__(self, path):
        self.file_path = path

        self.image = None
        self.height = None
        self.width = None
        self.channels = None

    def read(self, file=None):
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
        cv2.imwrite(out, self.image)
