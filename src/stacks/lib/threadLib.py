#!/usr/bin/python3
from PySide6.QtCore import QThread
import subprocess

class exeApp(QThread):
	def __init__(self,parent=None):
		super (exeApp,self).__init__(parent)
		self.app=None
	#def __init__

	def setApp(self,app):
		self.app=app
	#def setApp

	def run(self):
		subprocess.run(self.app,stdin=None,stdout=None,stderr=None,shell=False)
	#def run
#class exeApp

