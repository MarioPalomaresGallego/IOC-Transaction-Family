import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from hashlib import sha256

class S(BaseHTTPRequestHandler):

	def _set_response(self):

		self.send_response(200)
		self.end_headers()

	def do_GET(self):

		logging.info("GET request received")
		self._set_response()

	def do_POST(self):

		logging.info("POST request recieved")

		content_length = self.headers["Content-Length"]
		#Filter the body from the raw HTTP request
		payload = self.rfile.read(int(content_length))

		file_name = sha256(payload).hexdigest()
		logging.info("File name: " + file_name)
		if not os.path.exists("/tmp/" + file_name):
			with open("/tmp/" + file_name,"bx") as file:
				file.write(payload)

		self._set_response()

def run(server_class=HTTPServer, handler_class=S, port=8080):
	logging.basicConfig(level=logging.INFO)
	server_address = ('0.0.0.0', port)
	httpd = server_class(server_address, handler_class)
	logging.info('Starting httpd...\n')
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	logging.info('Stopping httpd...\n')


if __name__ == '__main__':
	from sys import argv
	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		run()

