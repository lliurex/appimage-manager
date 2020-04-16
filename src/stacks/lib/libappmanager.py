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
		oldDir=os.environ['PWD']
		os.chdir("/tmp")
		subprocess.run(["chmod","+x","%s"%app])
		output=subprocess.check_output(["%s"%app,"--appimage-extract","*.desktop"],stderr=subprocess.STDOUT)
		output=output.decode("utf-8").replace("\n","")
		if output.endswith("desktop"):
			try:
				with open(output,'r') as f:
					for line in f.readlines():
						if line.startswith("Exec"):
							data['exe']=line.split("=")[-1]
						if line.startswith("Name="):
							data['name']=line.split("=")[-1]
						if line.startswith("Icon"):
							data['icon']=line.split("=")[-1].strip()
						if line.startswith("Comment="):
							data['desc']=line.split("=")[-1]
			except Exception as e:
				print("getAppData: %s"%e)
		icn=''
		if data['icon']:
			output=subprocess.check_output(["%s"%app,"--appimage-extract","%s.svg"%data['icon']])
			if not output:
				output=subprocess.check_output(["%s"%app,"--appimage-extract","%s.png"%data['icon']],stderr=subprocess.STDOUT)
			if output:
				icn=os.path.join("/tmp",output.decode("utf-8").replace("\n",""))
				if os.path.islink(icn):
					output=subprocess.check_output(["%s"%app,"--appimage-extract","%s"%os.readlink(icn)])
					if output:
						icn=os.path.join("/tmp",output.decode("utf-8").replace("\n",""))
				if os.path.isfile(icn):
					self._debug("Icon found at %s"%icn)
					data['icon']=QIcon(icn)
				else:
					icn=''

		if not icn:
			icn="x-appimage"
			data['icon']=QIcon.fromTheme(icn)
#		try:
#			shutil.rmtree("/tmp","squashfs-root")
#		except Exception as e:
#			self._debug(e)
		os.chdir(oldDir)
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
