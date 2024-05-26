from pynput.mouse import Listener as MouseListener, Button
from time import time
import keyboard


class InputHandling:
    def __init__(self, app):
        self.app = app
        self.last_mouse_move_time = time()

    def start(self):
        def get_coords(x, y):
            if time() - self.last_mouse_move_time < 0.5:
                return
            [xmin, ymin, xmax, ymax] = self.app.gui.screen_dimensions
            if self.app.gui.focused and x > xmin and x < xmax and y > ymin and y < ymax:
                if self.app.debug:
                    print("DEBUG: Mouse ", x, y)
                relativeX = (x - xmin) / (xmax - xmin)
                relativeY = (y - ymin) / (ymax - ymin)
                self.app.send("MOUSE", "MOVE", relativeX, relativeY)
                self.last_mouse_move_time = time()

        def on_key_event(event):
            if not self.app.gui.focused:
                return
            if self.app.debug:
                print("DEBUG: Keyboard", event.name)
            self.app.send("KEYBOARD", event.name)

        def on_click(x, y, button, pressed):
            [xmin, ymin, xmax, ymax] = self.app.gui.screen_dimensions
            if self.app.gui.focused and x > xmin and x < xmax and y > ymin and y < ymax:
                if pressed:
                    if button == Button.left:
                        button_name = 'Left'
                    elif button == Button.right:
                        button_name = 'Right'
                    elif button == Button.middle:
                        button_name = 'Middle'
                    else:
                        button_name = 'Unknown'
                        return

                    if self.app.debug:
                        print("DEBUG: Mouse Click", button_name)
                    self.app.send("MOUSE", "CLICK", button_name)

        def on_scroll(x, y, dx, dy):
            [xmin, ymin, xmax, ymax] = self.app.gui.screen_dimensions
            if self.app.gui.focused and x > xmin and x < xmax and y > ymin and y < ymax:
                if self.app.debug:
                    print(f"DEBUG: Mouse scrolled at: ({dx}, {dy})")
                self.app.send("MOUSE", "SCROLL", dy)

        # Register listeners outside the start function
        mouse_listener = MouseListener(on_move=get_coords, on_click=on_click, on_scroll=on_scroll)
        self.mouse_listener = mouse_listener
        mouse_listener.start()

        keyboard.on_press(on_key_event)  # Register keyboard listener

        keyboard.wait('esc')  # Wait for ESC key press
        self.stopListening()

    def stopListening(self):
        self.mouse_listener.stop()
        keyboard.unhook_all()  # Unregister listeners
