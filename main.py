import sys
import asyncio
from structures import App, InputHandling, MouseKeyboardHandler, GUI

if __name__ == "__main__":
    # debug_mode = sys.argv[1]  # client | server
    app = App()
    app.debug = sys.flags.debug  # Show connection log to terminal
    gui = GUI(app)
    app.gui = gui

    try:
        gui.start()
    except KeyboardInterrupt:
        exit()
