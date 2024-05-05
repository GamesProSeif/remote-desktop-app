import pyautogui


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
            pyautogui.moveTo(x, y, duration=0.5)

    @staticmethod
    def keyboard(string):
        if string == "enter":
            pyautogui.hotkey('enter')
        else:
            pyautogui.typewrite(string)
