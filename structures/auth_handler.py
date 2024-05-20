class AuthHandler:
	def __init__(self, app):
		self.app = app
	
	def attempt_connection(self, code):
		if self.app.pass_code.lower() == code.lower():
			self.app.authenticated = True