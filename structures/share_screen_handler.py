from time import sleep
from PIL import Image
from io import BytesIO
import pyscreeze


class ScreenShareHandler:
	def __init__(self, app):
		self.app = app
		self.screen = pyscreeze
		self.frame_rate = 15  # frames per second

	def capture_and_send(self):
		delay = 1 / self.frame_rate
		while self.app.running:
			if self.app.authenticated:
				frame = self.screen.screenshot()
				frame_rgb = frame.convert("RGB")
				buffer = BytesIO()
				frame_rgb.save(buffer, "JPEG", quality=70)
				compressed_frame_data = buffer.getvalue()
				self.app.send("SCREEN", compressed_frame_data, frame_rgb.width, frame_rgb.height)
			sleep(delay)

	def receive(self, frame, width, height):
		# Known issue: Interleaved Data Streams
		if not isinstance(frame, bytes):
			frame = bytes(frame)
		frame_buffer = BytesIO(frame)
		self.app.gui.original_image = Image.open(frame_buffer)
		self.app.gui.adjust_image()
