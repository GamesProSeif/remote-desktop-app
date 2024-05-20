import re

class AuthHandler:
	def __init__(self, app):
		self.app = app
	
	def validate_link(self, text):
		pattern = r"^(?:[0-9]{1,3}\.){3}(?:[0-9]{1,3})\?p=([0-9a-f]{1,})"
		match = re.match(pattern, text)
		# Additional check for octets within 0-255 range
		if match:
			ip_bytes = text.split("?p=")[0].split(".")  # Split the IP into octets
			return all(0 <= int(octet) <= 255 for octet in ip_bytes)
		else:
			return False

	def check_pass_code(self, code):
		if self.app.pass_code.lower() == code.lower():
			self.app.authenticated = True
			return True
		return False