#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
import threading
import asyncore, socket

START_BAT = 'start.bat'

class async_http(asyncore.dispatcher):
	def __init__(self,port):
		asyncore.dispatcher.__init__(self)
		self.clients = []
		self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
		self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.bind(('',port))
		self.listen(5)

	def handle_accept(self):
		client,addr = self.accept()
		text.insert('0.0', 'connected by ' + str(addr[0]) + '\n')
		self.clients.append(async_handler(client, addr))
		return self.clients[-1]

	def disconnect(self, client):
		self.clients.remove(client)

	def start(self, fileName):
		for x in self.clients:
			x.setText('start ' + fileName)
  
	def kill(self):
		for x in self.clients:
			x.setText('kill')

	def reboot(self):
		for x in self.clients:
			x.setText('reboot')
	
	def shutdown(self):
		for x in self.clients:
			x.setText('shutdown')

class async_handler(asyncore.dispatcher):
	def __init__(self, sock = None, addr=None):
		asyncore.dispatcher.__init__(self,sock)
		self.addr = addr
		self.buffer = b'connect'

	def handle_write(self):
		sent = self.send(self.buffer)
		self.buffer = self.buffer[sent:]

	def writable(self):
		return (len(self.buffer) > 0)

	def handle_read(self):
		chunk = self.recv(8192)
		if not chunk:
			text.insert('0.0', str(self.addr[0]) + ' disconnected\n')

	def handle_close(self):
		a.disconnect(self)
		self.close()

	def __del__(self):
		self.close()

	def setText(self, text):
		self.buffer = bytes(text.encode('ascii'))[:]

class Connect(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
	def run (self):
		asyncore.loop(timeout=0.1)

#interface
def clickStart(event):
	a.start(START_BAT)
def clickKill(event):
	a.kill()
def clickReboot(event):
	a.reboot()
def clickShutdown(event):
	a.shutdown()

root = Tk()
content = Frame(root)

def callback():
	if askokcancel("Quit", "Do you really wish to quit?"):
		root.destroy()

text = Text(content, width=50, height=15, wrap="word")
text.pack()
scrollbar = Scrollbar(text)
scrollbar['command'] = text.yview
text['yscrollcommand'] = scrollbar.set

content.pack(expand=1)
buttons = Frame(root)
buttons.pack(side="bottom", fill = 'x')

start = Button(buttons, text=u"Старт")
start.pack(side = 'left')
start.bind("<Button-1>", clickStart)
stop = Button(buttons, text=u"Стоп")
stop.pack(side = 'left')
stop.bind("<Button-1>", clickKill)
restart = Button(buttons, text=u"Перезагрузка")
restart.pack(side = 'left')
restart.bind("<Button-1>", clickReboot)
shutDown = Button(buttons, text=u"Выключение")
shutDown.pack(side = 'left')
shutDown.bind("<Button-1>", clickShutdown)
#end interface

a = async_http(9999)
Connect().start()
root.protocol("WM_DELETE_WINDOW", callback)
root.mainloop()
del a
print('end')