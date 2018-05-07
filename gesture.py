# imports - third-party packages
import numpy as np
import math
import cv2
import pyautogui

# imports - module imports
from base import Event, Util

_DEFAULT_GAUSSIAN_BLUR_KERNEL = (35, 35)
_DEFAULT_THRESHOLD_TYPE       = cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU

_COLOR_RED   = (0, 0, 255)
_COLOR_GREEN = (0, 255, 0)
_COLOR_GREEN = (0, 255, 0)

def _get_contours(array):
    major = Util.get_opencv_version()[0]

    if major == 3:
        _, contours, _ = cv2.findContours(array, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    else:
        _, contours    = cv2.findContours(array, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    return contours

def _draw_contours(array, *args, **kwargs):
    cv2.drawContours(array, *args, **kwargs)

def _get_eucledian_distance(a, b):
    distance = math.sqrt( (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    return distance

def _get_defects_count(array, contour, defects, verbose = False):
    ndefects = 0
    
    for i in range(defects.shape[0]):
        s,e,f,_ = defects[i,0]
        beg     = tuple(contour[s][0])
        end     = tuple(contour[e][0])
        far     = tuple(contour[f][0])
        a       = _get_eucledian_distance(beg, end)
        b       = _get_eucledian_distance(beg, far)
        c       = _get_eucledian_distance(end, far)
        angle   = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) # * 57
            
        if angle <= math.pi/2 :#90:
            ndefects = ndefects + 1

            if verbose:
                cv2.circle(array, far, 3, _COLOR_RED, -1)

        if verbose:
            cv2.line(array, beg, end, _COLOR_RED, 1)

    return array, ndefects

def _get_tip_position(array, contour, verbose = False):
    approx_contour = cv2.approxPolyDP(contour, 0.08 * cv2.arcLength(contour, True), True)
    convex_points  = cv2.convexHull(approx_contour, returnPoints = True)
    
    cx, cy     = 999, 999

    for point in convex_points:
        cur_cx, cur_cy = point[0][0], point[0][1]

        if verbose:
            cv2.circle(array, (cur_cx, cur_cy), 4, _COLOR_GREEN,4)
            
        if (cur_cy < cy):
            cx, cy = cur_cx, cur_cy

    (screen_x, screen_y) = pyautogui.size()

    height, width, _ = array.shape
    x = Util.round_int((float(cx))/(width-0)*(screen_x+1))
    y = Util.round_int((float(cy))/(height-0)*(screen_y+1))
    return (array, (x, y))

def _remove_background(frame):
    fgbg = cv2.createBackgroundSubtractorMOG2()
    # fgmask = bgModel.apply(frame)
    fgmask = fgbg.apply(frame)
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    # res = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=fgmask)
    return res

def _bodyskin_detetc(frame):
    # 肤色检测: YCrCb之Cr分量 + OTSU二值化
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb) # 分解为YUV图像,得到CR分量
    (_, cr, _) = cv2.split(ycrcb)
    cr1 = cv2.GaussianBlur(cr, (5, 5), 0) # 高斯滤波
    _, skin = cv2.threshold(cr1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # OTSU图像二值化
    return skin

def grdetect(array, verbose = False):
    event      = Event(Event.NONE)

    copy       = array.copy()

    array = _remove_background(array) # 移除背景, add by wnavy
    '''
    gray       = Util.to_grayscale(array) # 转化为灰度图像
    blur       = cv2.GaussianBlur(gray, ksize = _DEFAULT_GAUSSIAN_BLUR_KERNEL, sigmaX = 0) # 高斯滤波
    _, thresh  = cv2.threshold(blur, 0, 255, _DEFAULT_THRESHOLD_TYPE) # 图像二值化
    '''
    thresh = _bodyskin_detetc(array)

    if verbose:
        cv2.imshow('pygr.HoverPad.roi.threshold', thresh)

    contours   = _get_contours(thresh.copy())
    largecont  = max(contours, key = lambda contour: cv2.contourArea(contour))

    if verbose:
        roi  = cv2.boundingRect(largecont)
        copy = Util.mount_roi(copy, roi, color = _COLOR_RED)

    convexHull = cv2.convexHull(largecont)

    if verbose:
        _draw_contours(copy, contours    ,-1, _COLOR_RED  , 0)
        _draw_contours(copy, [largecont] , 0, _COLOR_GREEN, 0)
        _draw_contours(copy, [convexHull], 0, _COLOR_GREEN, 0)

    hull           = cv2.convexHull(largecont, returnPoints = False)
    defects        = cv2.convexityDefects(largecont, hull)
        
    if defects is not None:
        copy, ndefects = _get_defects_count(copy, largecont, defects, verbose = verbose)
        if   ndefects == 0:
            copy, tip  = _get_tip_position(copy, largecont, verbose = verbose)

            event.setTip(tip)
            # TODO: check for a single finger.
            # event.setType(Event.ROCK)
            event.setType(Event.ZERO)
        elif ndefects == 1:
            # TODO: check for an Event.LIZARD
            # event.setType(Event.SCISSOR)
            event.setType(Event.TWO)
        elif ndefects == 2:
            # event.setType(Event.SPOCK)
            event.setType(Event.THREE)
        elif ndefects == 3:
            event.setType(Event.FOUR)
        elif ndefects == 4:
            # event.setType(Event.PAPER)
            event.setType(Event.FIVE)
    if verbose:
        cv2.imshow('pygr.HoverPad.roi', copy)

    if verbose:
        return copy, event
    else:
        return event