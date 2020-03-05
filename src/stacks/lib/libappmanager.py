#!/usr/bin/python3
import os
import shutil
import subprocess
from PyQt5.QtGui import QIcon

class appmanager():
	def __init__(self):
		self.dbg=True
		self.appPath="%s/Applications"%os.environ["HOME"]

	def _debug(self,msg):
		if self.dbg:
			print("%s"%msg)
	#def _debug
	
	def getAppData(self,app):
		data={'name':'','desc':'','exe':'','icon':''}
		subprocess.run(["chmod","+x","%s"%app])
		output=subprocess.check_output(["%s"%app,"--appimage-extract","*.desktop"])
		output=output.decode("utf-8")
		with open(output.replace("\n",""),'r') as f:
			for line in f.readlines():
				if line.startswith("Exec"):
					data['exe']=line.split("=")[-1]
				if line.startswith("Name="):
					data['name']=line.split("=")[-1]
				if line.startswith("Icon"):
					data['icon']=line.split("=")[-1].strip()
				if line.startswith("Comment="):
					data['desc']=line.split("=")[-1]
		if data['icon']:
			output=subprocess.check_output(["%s"%app,"--appimage-extract","%s.svg"%data['icon']])
			if not output:
				output=subprocess.check_output(["%s"%app,"--appimage-extract","%s.png"%data['icon']])
			if output:
				icn=output.decode("utf-8").replace("\n","")
				data['icon']=QIcon("./%s"%icn)

		if not data['icon']:
			icn="x-appimage"
			data['icon']=QIcon.fromTheme(icn)
		return(data)
	#def _getAppData

	def localInstall(self,app):
		retval=False
		if not os.path.isdir(self.appPath):
			try:
				os.makedirs(self.path)
			except:
				err=True
		if os.path.isfile(app):
			try:
				shutil.copyfile(app,os.path.join(self.appPath,os.path.basename(app)))
				retval=True
			except Exception as e:
				self._debug(e)
		return(retval)
	#def localInstall

	def localRemove(self,app):
		retval=False
		if os.path.isfile(app):
			try:
				os.remove(app)
				retval=True
			except Exception as e:
				self._debug(e)
		return(retval)
