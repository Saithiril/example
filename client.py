#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
import threading
import asyncore, socket
import subprocess, os, sys

SERVER = '192.168.0.216'
SERVER_PORT = 9999

#interface
root = Tk()
content = Frame(root)

text = Text(content, width=50, height=15, wrap="word")
text.pack()
scrollbar = Scrollbar(text)
scrollbar['command'] = text.yview
text['yscrollcommand'] = scrollbar.set
content.pack(expand=1)
#end interface

class async_client(asyncore.dispatcher):
	def __init__(self,port):
		self.disconnected = True
		self.buffer = b''
		self.process = None
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
		self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.got_request = False
		self.connect((SERVER, port))
  
	def handle_close(self):
		self.disconnected or text.insert('0.0', "disconnecting\n")
		self.close()
		self.disconnected = True
		self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
		self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.connect((SERVER, SERVER_PORT))

	def handle_connect(self):
		pass

	def handle_error(self):
		pass

	def handle_write(self):
		sent = send(self.buffer)
		self.buffer = self.buffer[sent:]
		text.insert('0.0', self.buffer)

	def handle_read(self):
		chunk = self.recv(8192)
      
		if chunk == b'connect':
			text.insert('0.0', 'connected to server\n')
			self.disconnected = False
		elif 'start' in chunk.decode('ascii'): self.startProcess(chunk.decode('ascii').strip().split()[1])
		elif 'kill' in chunk.decode('ascii'): self.killProcess()
		elif 'reboot' in chunk.decode('ascii'): self.reboot()
		elif 'shutdown' in chunk.decode('ascii'): self.shutdown()

	def writable(self):
		return (len(self.buffer) > 0)
	
	def startProcess(self, params):
		if not self.process:
			fullName = os.path.join(os.path.dirname(sys.argv[0]), params)
			if not os.path.exists(fullName):
				text.insert('0.0', 'file {0} not found\n'.format(fullName))
				return
			a = open(fullName, mode='r').readlines()
			self.process = subprocess.Popen(*a, universal_newlines = True)
		else:
			text.insert('0.0', 'process already running\n')

	def killProcess(self):
		text.insert('0.0', "killing process\n")
		self.process.kill()
		self.process = None

	def reboot(self):
		#reboot for windows
		subprocess.call('shutdown /r')
	def shutdown(self):
		#shutdown for windows
		subprocess.call('shutdown /s')

def callback():
	#if askokcancel("Quit", "Do you really wish to quit?"):
	root.destroy()

class Connect(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
	def run (self):
		asyncore.loop(timeout=0.1)
    
a = async_client(SERVER_PORT)
Connect().start()
root.protocol("WM_DELETE_WINDOW", callback)
root.mainloop()
print ("end")