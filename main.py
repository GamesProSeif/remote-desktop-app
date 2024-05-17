import sys
import asyncio
from structures import App, InputHandling, MouseKeyboardHandler, GUI

# to run server "$ py main.py server"
# to run client "$ py main.py client"
if __name__ == "__main__":
    app_mode = sys.argv[1]  # client | server
    app = App()
    app.setMode(app_mode)
    app.debug = True  # Show connection log to terminal
    inputhandling = InputHandling(app)
    mouseKeyboardHandler = MouseKeyboardHandler()
    gui = GUI(app)
    if app.mode == "client":
        app.addListener(inputhandling.start)
    else:    
        app.addHandler("MOUSE", mouseKeyboardHandler.mouse)
        app.addHandler("KEYBOARD", mouseKeyboardHandler.keyboard)

    app.startGUI(gui)

    try:
        app.start()
    except KeyboardInterrupt:
        exit()
