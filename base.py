# imports - standard imports
import io
import base64

# imports - third-party imports
import numpy as np
from PIL import Image
import cv2


class Config(object):
    NAME = 'pygr'
    VERSION = '0.1.0'
    PyGR_SIZE = (480, 320)


class Keycode(object):
    ESCAPE = 27
    Q = ord('Q')
    q = ord('q')


class Event(object):
    '''
    Event object
    '''
    NONE = None
    ROCK = 0  # 石头
    SCISSOR = 1  # 剪刀
    SPOCK = 2
    PAPER = 4  # 布

    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    def __init__(self, type_=None):
        self.type = type_
        self.tip = (None, None)

    def setType(self, type_):
        self.type = type_

    def setTip(self, position):
        self.tip = position

    def get_tip(self):
        return self.tip


class Util(object):
    @staticmethod
    def resize_image(image, size, maintain_aspect_ratio=False):
        copy = image.copy()
        copy.thumbnail(size, Image.ANTIALIAS)
        return copy

    @staticmethod
    def round_int(value):
        result = int(np.rint(value))
        return result

    @staticmethod
    def to_grayscale(array):
        gray = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
        return gray

    @staticmethod
    def get_opencv_version():
        version = cv2.__version__
        version = version.split('.')
        major, minor, patch = int(version[0]), int(version[1]), int(version[2])
        return (major, minor, patch)

    @staticmethod
    def mount_roi(array, roi, color=(0, 255, 0), thickness=1):
        x, y, w, h = roi
        cv2.rectangle(array, (x, y), (x + w, y + h),
                      color=color, thickness=thickness)
        return array

    @staticmethod
    def image_to_bytes(image, format_='.jpg'):
        array = np.asarray(image)
        _, jpeg = cv2.imencode(format_, array)
        bytes_ = jpeg.tobytes()
        return bytes_

    @staticmethod
    def base64_str_to_image(string):
        decode = base64.b64decode(string)
        bytes_ = io.BytesIO(decode)
        image = Image.open(bytes_)
        return image


class Capture(object):
    '''
    Capture object

    :param deviceID: device ID of your capture device, defaults to 0
    :type deviceID: :obj:`int`

    Example

    >>> import pygr
    >>> cap = pygr.Capture()
    '''

    def __init__(self, deviceID=0):
        self.deviceID = deviceID
        self.capture = cv2.VideoCapture(self.deviceID)

    def read(self):
        '''
        Reads the current input stream from a capture device and returns a `PIL.Image` object

        >>> import pygr
        >>> cap   = pygr.Capture()
        >>> image = cap.read()
        >>> image.show()
        '''
        _, frame = self.capture.read()
        frame = cv2.bilateralFilter(frame, 5, 50, 100)  # 双边滤波
        image = Image.fromarray(frame)

        return image
