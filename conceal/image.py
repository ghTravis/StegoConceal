import cv2


class Image(object):
    def __init__(self, path):
        self.file_path = path

        self.image = None
        self.height = None
        self.width = None
        self.channels = None

    def read(self, file=None):
        self.image = cv2.imread(file or self.file_path)
        self.height, self.width, self.channels = self.image.shape

