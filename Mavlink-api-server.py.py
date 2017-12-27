import argparse
import cgi
import logging
import os
import sys

import json
import jsonpickle



from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

autoPilotData = {}

class Server_Request_Handler(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.send_header('Access-Control-Allow-Origin', '*')
		self.end_headers()

	def do_GET(self):
		global autoPilotData
		self._set_headers()
		
		if self.path.split('?')[0] == '/autoPilotData':
			self.wfile.write(autoPilotData)

		#elif self.path == '/params':
		#	self.wfile.write(params)

	def do_POST(self):
		global autoPilotData
		self._set_headers()

		self.data_string = self.rfile.read(int(self.headers['Content-Length']))
		
		if self.path == '/autoPilotData':
			autoPilotData = self.data_string
			#print('data :', autoPilotData)
			self.wfile.write('{"message": "posted"}')

		elif self.path == '/params':
			self.wfile.write(params)
				

def run(server_class=HTTPServer, handler_class=Server_Request_Handler, port=80):

	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	try:
		print("Starting httpd... ")
		httpd.serve_forever()
	except:
		pass
	finally:
		httpd.server_close()
		sys.exit()

		
if __name__ == "__main__":
	from sys import argv

	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		run()
