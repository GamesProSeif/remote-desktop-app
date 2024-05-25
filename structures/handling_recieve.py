import pyautogui
from screeninfo import get_monitors

[screenWidth, screenHeight] = [
    [screen.width, screen.height] for screen in get_monitors() if screen.is_primary
][0]

class MouseKeyboardHandler:
    @staticmethod
    def mouse(event_type, *args):
        if event_type == "CLICK":
            if args[0] == "Right":
                pyautogui.click(button='right')
            else:
                pyautogui.click(button='left')
        elif event_type == "SCROLL":
            if args[0] > 0:
                pyautogui.scroll(200)
            else:
                pyautogui.scroll(-200)
        elif event_type == "MOVE":
            x, y = args[:2]
            physicalX = x * screenWidth
            physicalY = y * screenHeight
            pyautogui.moveTo(physicalX, physicalY, duration=0.1)

    @staticmethod
    def keyboard(string):
        if string == "enter":
            pyautogui.hotkey('enter')
        else:
            pyautogui.typewrite(string)
