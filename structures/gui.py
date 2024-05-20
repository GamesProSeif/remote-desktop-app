import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pyperclip import copy as copy_to_clipboard


class GUI:
	def __init__(self, app):
		self.app = app

		self.geometry = "800x600"

		self.root = tk.Tk()
		self.root.title("Remote Desktop App")
		self.root.geometry(self.geometry)

		self.main_frame = tk.Frame(self.root)
		self.main_frame.pack(fill='both', expand=True)

		self.label3=tk.Label(self.main_frame,text="Choose Server or Client",relief="solid",font=("arial",16,"bold"))
		self.label3.pack(pady=20)

		self.btn_server = tk.Button(self.main_frame, text="Server",fg='blue',bg='white',relief="ridge",command=self.show_server_page)
		self.btn_server.pack(pady=20)

		self.btn_client = tk.Button(self.main_frame, text="Client",fg='blue',bg='white',relief="ridge",command=self.show_client_page)
		self.btn_client.pack(pady=20)

		self.client_frame = tk.Frame(self.root)
		self.link_entry = tk.Entry(self.client_frame)
		self.link_entry.pack(pady=20, padx=100, fill='x', expand=True)

		self.connect_button = tk.Button(self.client_frame, text="Connect", command=self.connect_to_server)
		self.connect_button.pack(pady=20)


		# self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

	def init_server_gui(self):
		self.server_root = tk.Tk()
		self.server_root.title("Remote Desktop App | Server")
		self.server_root.geometry(self.geometry)

		self.server_frame = tk.Frame(self.server_root)

		self.label4=tk.Label(self.server_frame,text="Share Link",fg='blue',bg='white',font=("arial",16,"bold"))
		self.label4.pack(pady=100)

		self.password_entry = tk.Entry(self.server_frame)
		self.password_entry.pack(pady=20, padx=50, fill='x', expand=True)

		self.copy_link_button = tk.Button(self.server_frame, text="Copy Link", command=self.copy_link)
		self.copy_link_button.pack(pady=20)
		self.server_root.protocol("WM_DELETE_WINDOW", self.on_window_close)

	def init_client_gui(self):
		self.client_root = tk.Tk()
		self.client_root.title("Remote Desktop App | Client")
		self.client_root.geometry(self.geometry)

		self.connected_client_page = tk.Frame(self.client_root)
		self.connected_client_page.bind('<Configure>', self.adjust_image)  # Bind resize event

		self.tools_frame = tk.Frame(self.connected_client_page)
		self.tools_frame.pack(fill='x')

		self.disconnect_button = tk.Button(self.tools_frame, text="Disconnect", command=self.disconnect)
		self.disconnect_button.pack(side='left', padx=10)

		self.file_transfer_button = tk.Button(self.tools_frame, text="File Transfer")
		self.file_transfer_button.pack(side='left', padx=10)

		self.chat_button = tk.Button(self.tools_frame, text="Chat")
		self.chat_button.pack(side='left', padx=10)

		self.image_path = "city.jpg"
		self.original_image = Image.open(self.image_path)

		self.screen_area = tk.Label(self.connected_client_page)
		self.screen_area.pack(fill='both', expand=True)
		self.client_root.protocol("WM_DELETE_WINDOW", self.on_window_close)

	def start(self):
		self.root.mainloop()

	def adjust_image(self, event=None):
		# Calculating new size maintaining 16:9 aspect ratio
		new_width = self.connected_client_page.winfo_width()
		if new_width < 5:
			new_width = 800
		new_height = int(new_width * 9 / 16)

		# Resize the image using Pillow
		resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
		photo_image = ImageTk.PhotoImage(resized_image)

		# Update the label image
		self.screen_area.config(image=photo_image)
		self.screen_area.image = photo_image  # Keep a reference!

	def disconnect(self):
		self.root.destroy()

	def show_server_page(self):
		self.app.setMode("server")
		self.main_frame.pack_forget()
		self.root.destroy()
		self.init_server_gui()
		self.app.startGUI(self)
		self.server_frame.pack(fill='both', expand=True)

		self.app.generate_pass_code()
		self.password_entry.delete(0, tk.END)
		self.password_entry.insert(0, self.app.get_link())

		self.app.start()

	def show_client_page(self):
		self.main_frame.pack_forget()
		self.client_frame.pack(fill='both', expand=True)

	def show_client_page(self):
		self.main_frame.pack_forget()
		self.client_frame.pack(fill='both', expand=True)

	def copy_link(self):
		copy_to_clipboard(self.app.get_link())
		old_text = self.copy_link_button.config()["text"][4]
		self.copy_link_button.config(text="Copied to Clipboard")
		self.server_root.after(1500, lambda: self.copy_link_button.config(text=old_text))

	def connect_to_server(self):
		self.app.setMode("client")
		self.client_frame.pack_forget()
		self.root.destroy()
		self.init_client_gui()
		self.app.startGUI(self)
		self.connected_client_page.pack(fill='both', expand=True)
		self.adjust_image()
		self.app.start()

	def on_window_close(self):
		self.app.stop()
