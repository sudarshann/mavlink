from __future__ import print_function
from builtins import range

import sys
import json
import jsonpickle
import requests
import time

from pymavlink import mavutil


from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer



class MavLinkParser(object):
	
	def __init__(self):
		self.shutdownFlag = False
		self.master = ""
		self.time = time.time()
		
	def read_loop(self):
		
		while(True and not self.shutdownFlag):

			# grab a mavlink message
			msg = self.master.recv_match(blocking=False)
			if not msg:
				continue

			# handle the message based on its type
			msg_type = msg.get_type()
			if msg_type == "BAD_DATA":
				if mavutil.all_printable(msg.data):
					sys.stdout.write(msg.data)
					sys.stdout.flush()
			elif msg_type == "HEARTBEAT":
				self.handle_heartbeat(msg)
			
			messagesFormated = {}
			for k, v in self.master.messages.iteritems():
				if k == "MAV": continue
				if k == "PARAM_VALUE": continue
				messagesFormated[k] = v.to_dict()

			#global messages
			#messages = jsonpickle.encode(messagesFormated, unpicklable=False)
					
			#global params
			#params = jsonpickle.encode(self.master.params, unpicklable=False)

			formattedData = {}
			formattedData['params'] = self.master.params
			formattedData['messages'] = messagesFormated
			
			formattedData = jsonpickle.encode(formattedData, unpicklable=False)

			currentTime = time.time()
			if currentTime - self.time > 0.5:
				self.time = currentTime
				try:
					requests.post("http://127.0.0.1/autoPilotData", data=formattedData)
				except:
					print("Unexpected error:", sys.exc_info())
					pass
				
				 
	def handle_heartbeat(self,msg):
		mode = mavutil.mode_string_v10(msg)
		is_armed = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
		is_enabled = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_GUIDED_ENABLED

	def shutdown(self):
		self.shutdownFlag = True
		if(self.master != ''):
			self.master.close()
	
	def wait_heartbeat(self):
		'''wait for a heartbeat so we know the target system IDs'''
		print("Waiting for APM heartbeat")
		self.master.wait_heartbeat()
		print("Heartbeat from APM (system %u component %u)" % (self.master.target_system, self.master.target_system))

	def run(self, port="com3"):
		try:
			self.shutdownFlag = False
		
			# create a mavlink serial instance
			self.master = mavutil.mavlink_connection(port, baud=115200, autoreconnect=True)
			self.master.setup_logfile("log.tlog", "w")

			# wait for the heartbeat msg to find the system ID
			self.wait_heartbeat()
		
			print("Sending all stream request for rate %u" % 5)
			for i in range(0, 3):
				self.master.mav.request_data_stream_send(self.master.target_system, self.master.target_component,
												mavutil.mavlink.MAV_DATA_STREAM_ALL, 5, 1)

			self.master.param_fetch_all()
		
			self.read_loop()
		except:
			print("Unexpected error:", sys.exc_info())
			self.shutdown()		
				
		
if __name__ == "__main__":
	from sys import argv
	mavLinkParser = MavLinkParser()
	if len(argv) == 2:
		mavLinkParser.run(port=argv[1])
	else:
		mavLinkParser.run()
