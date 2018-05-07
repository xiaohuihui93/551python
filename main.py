# imports - app imports
import pygr
import cv2
import time
from base import Keycode, Event
import pyautogui


if __name__ == '__main__':
    pad = pygr.PyGR(size = (480, 320), verbose = True)
    #pad = pygr.PyGR(size = (480, 320))
    pad.show()
    while cv2.waitKey(10) not in [Keycode.ESCAPE, Keycode.Q, Keycode.q]:
        event = pad.get_event()
        print("Event:", event.type, "Tip:", event.tip)
        if event.type == Event.ZERO :
            pyautogui.scroll(-50) # scroll down 10 "clicks"
        elif event.type == Event.TWO :
            pyautogui.scroll(50) # scroll up 10 "clicks"
        elif event.type == Event.THREE :
            pyautogui.hotkey('alt','left')
        elif event.type == Event.FOUR :
            pyautogui.hotkey('alt','right')
        elif event.type == Event.FIVE :
            pyautogui.hotkey('alt','f4')
        time.sleep(0.5)
    
