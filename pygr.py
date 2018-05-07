# imports - standard imports
import threading

# imports - third-party imports
import numpy as np
import cv2
from PIL import Image

# imports - module imports
from base          import Config, Event, Keycode, Capture, Util
from gesture       import grdetect

def _get_roi(size, ratio = 0.42, position = 'tl'):
    '''
    根据缩放比计算指定的举行区域的坐标

    Parameters
    :param size: 图像大小
    :param ratio: 缩放比
    :param position: 缩放方式
    '''
    width, height = Util.round_int(size[0] * ratio), Util.round_int(size[1] * ratio)

    if   position == 'tl':
        x, y = 0, 0
    elif position == 'tr':
        x, y = size[0] - width, 0
    elif position == 'bl':
        x, y = 0, size[1] - height
    elif position == 'br':
        x, y = size[0] - width, size[1] - height

    return (x, y, width, height)

def _crop_array(array, roi):
    '''
    裁剪目标图像中指定的举行区域

    Parameters
    :param array: 目标图像
    :param roi: 指定的矩形区域
    '''
    x, y, w, h = roi
    crop       = array[ y : y + h , x : x + w ]

    return crop

class PyGR(object):
    '''
    PyGR object

    Parameters

    :param size: the size of the PyGR instance containing the width and height in pixels, defaults to 320x240
    :type size: :obj:`tuple`

    :param deviceID: the device ID of your capture device, defaults to 0.
    :type deviceID: :obj:`int`

    :param position: the relative position of the :obj:`PyGR` with respect to the current frame. This could be top-left (`tl`), top-right (`tr`), bottom-left (`bl`) and bottom-right (`br`)
    :type position: :obj:`str`, defaults to `tl`.

    :param verbose: if True, displays frames containing the threshold and contour information.
    :type verbose: :obj:`bool`

    Example

    >>> import pygr
    >>> pad = pygr.PyGR(size = (480, 320), verbose = True)
    '''
    TITLE = 'PyGR | pygr'

    def __init__(self, size = Config.PyGR_SIZE, deviceID = 0, position = 'tl', verbose = False):
        self.size     = size
        self.deviceID = deviceID
        self.capture  = Capture(deviceID = self.deviceID)
        self.position = position
        self.event    = Event(Event.NONE)
        self.image    = None

        self.verbose  = verbose

        self.roi      = _get_roi(size = self.size, ratio = 0.65, position = position)

        self.thread   = threading.Thread(target = self._showloop)

    def show(self):
        '''
        Displays the PyGR object instance onto the screen. To close the PyGR, simply press the ESC key
        
        Example

        >>> import pygr
        >>> pad = pygr.PyGR()
        >>> pad.show()
        '''
        self.thread.start()

    def _showloop(self):
        while cv2.waitKey(10) not in [Keycode.ESCAPE, Keycode.Q, Keycode.q]:
            image = self.capture.read()
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

            image = Util.resize_image(image, self.size)
            
            array = np.asarray(image)
            array = Util.mount_roi(array, self.roi, color = (74, 20, 140), thickness = 2)

            crop  = _crop_array(array, self.roi)

            # process image for any gestures
            if self.verbose:
                segments, event = grdetect(crop, verbose = self.verbose)
                self.image = Image.fromarray(segments)
                self.event = event
            else:
                event           = grdetect(crop, verbose = self.verbose)
                #self.image = Image.fromarray(segments)
                self.event = event
            #self.image = Image.fromarray(segments)
            #self.event = event
            cv2.imshow(PyGR.TITLE, array)
        cv2.destroyWindow(PyGR.TITLE)

    def get_event(self):
        '''
        Returns a :py:class:`pygr.Event` captured within the current frame.

        Example

        >>> import pygr
        >>> pad   = pygr.PyGR()
        >>> event = pad.get_event()
        >>> event.type == Event.ROCK
        True
        '''
        return self.event

    def get_image(self):
        '''
        Returns a :obj:`PIL.Image` captured within the current frame.

        Example
        
        >>> import pygr
        >>> pad   = pygr.PyGR()
        >>> image = pad.get_image()
        >>> image.show()
        '''
        return self.image
