import sys
import asyncio
from structures import App, InputHandling, MouseKeyboardHandler, GUI

# to run server "$ py main.py server"
# to run client "$ py main.py client"
if __name__ == "__main__":
    # app_mode = sys.argv[1]  # client | server
    app = App()
    # app.setMode(app_mode)
    app.debug = True  # Show connection log to terminal
    gui = GUI(app)
    app.gui = gui

    try:
        gui.start()
        # app.startGUI(gui)
        # app.start()
    except KeyboardInterrupt:
        exit()
