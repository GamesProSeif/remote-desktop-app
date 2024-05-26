from time import sleep
from tkinter import filedialog
from os import path, environ, makedirs

class FileHandler:
	def __init__(self, app):
		self.app = app

	def choose_file(self):
		self.app.send("HANDLER", "file_dialog_open")
		filename = filedialog.askopenfilename(title="Select file to transfer")
		self.app.send("HANDLER", "file_dialog_close")

		if filename:
			self.send_file_to_server(filename)

	def send_file_to_server(self, filepath):
		with open(filepath, "rb") as file:
			data = file.read()
			filename = filepath.split("/")[-1]
			# self.app.protocol.transport.write("stop_share_screen".encode())
			# sleep(1)
			self.app.send("FILE", filename, data)

	def receive_file(self, filename, data):
		downloads_folder = path.join("C:", environ.get('HOMEPATH'), 'Downloads')

		file_path = path.join(downloads_folder, filename)

		makedirs(downloads_folder, exist_ok=True)

		with open(file_path, 'wb') as file:
			file.write(data)
		
		self.app.screen_share_handler.active = True