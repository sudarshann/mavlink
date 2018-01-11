import argparse
import cgi
import logging
import os
import sys

import random

import json
import jsonpickle

from urlparse import urlparse, parse_qs
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

autoPilotData = {}
dataQueue = []


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
		elif self.path.split('?')[0] == '/autoPilotDataTest':
			
			with open('apm-sample-data.json') as json_data:
				#print(json_data.read())
				d = json.loads(json_data.read())
				#print("data" , d)
				#print("random data: ", random.choice(d))
				self.wfile.write(jsonpickle.encode(random.choice(d)))


	def do_POST(self):
		global autoPilotData
		global dataQueue
		
		self._set_headers()

		self.data_string = self.rfile.read(int(self.headers['Content-Length']))
		
		if self.path == '/autoPilotData':
			autoPilotData = self.data_string
			#print('data :', autoPilotData)
			self.wfile.write(jsonpickle.encode(dataQueue))
			dataQueue=[]
		
		elif self.path == '/setServo':
			query_components = jsonpickle.decode(self.data_string)
			
			channel = query_components["channel"]
			value = query_components["value"]
			
			servo = {}
			servo['channel'] = channel
			servo['value'] = value
			servo['type'] = "servo"
			
			dataQueue.append(servo);
			
			self.wfile.write("Data Queued. Servo Channel: " + str(channel) + " & Value: " + str(value))
			
		elif self.path == '/setRelay':
			query_components = jsonpickle.decode(self.data_string)
			
			channel = query_components["channel"]
			value = query_components["value"]
			
			relay = {}
			relay['channel'] = channel
			relay['value'] = value
			relay['type'] = "relay"
			
			dataQueue.append(relay);
			
			self.wfile.write("Data Queued. Servo Channel: " + str(channel) + " & Value: " + str(value))
				

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
