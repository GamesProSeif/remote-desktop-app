import sys
from structures import App


def take_file_input():
    flag = True
    while flag:
        try:
            # input delay to simulate listening for mouse actions
            input("Press Enter to send file example")
            in_file = open("main.py", "rb")
            data = in_file.read()
            in_file.close()
            app.send("FILE", data)
        except EOFError:
            flag = False


def fileHandler(data):
    print(f"file data {data}")


def take_mouse_input():
    flag = True
    while flag:
        try:
            # input delay to simulate listening for mouse actions
            input("Press Enter to send mouse example")
            app.send("MOUSE", 50, 60)
        except EOFError:
            flag = False


def mouseHandler(mouseX, mouseY):
    print(f"mouseX: {mouseX}\tmouseY: {mouseY}")


# to run server "$ py main.py server"
# to run client "$ py main.py client"
if __name__ == "__main__":
    app_mode = sys.argv[1]  # client | server
    app = App()
    app.setMode(app_mode)
    app.debug = True  # Show connection log to terminal

    # app.addListener(take_mouse_input)
    # app.addHandler("MOUSE", mouseHandler)

    app.addListener(take_file_input)
    app.addHandler("FILE", fileHandler)

    try:
        app.start()
    except KeyboardInterrupt:
        exit()
