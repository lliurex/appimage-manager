#!/usr/bin/python3
import os
import shutil
import subprocess
from PySide6.QtGui import QIcon

class appmanager():
	def __init__(self):
		self.dbg=True
		self.appPath=os.path.join(os.environ["HOME"],"Applications")

	def _debug(self,msg):
		if self.dbg:
			print("Appimage: {}".format(msg))
	#def _debug
	
	def getAppData(self,app):
		data={'name':'','desc':'','exe':'','icon':''}
		oldDir=os.environ['PWD']
		os.chdir("/tmp")
		subprocess.run(["chmod","+x",app])
		subprocess.run([app,"--appimage-extract","*.desktop"],stderr=subprocess.STDOUT)
		output=""
		if os.path.exists("/tmp/squashfs-root"):
			for f in os.scandir("/tmp/squashfs-root"):
				if f.name.endswith(".desktop"):
					output=f.path
		if output.endswith("desktop"):
			try:
				with open(output,'r') as f:
					for line in f.readlines():
						if line.startswith("Exec"):
							data['exe']=line.split("=")[-1].strip()
						if line.startswith("Name="):
							data['name']=line.split("=")[-1].strip()
						if line.startswith("Icon"):
							data['icon']=line.split("=")[-1].strip()
						if line.startswith("Comment="):
							data['desc']=line.split("=")[-1].strip()
			except Exception as e:
				print("getAppData: %s"%e)
		icn=''
		if data['icon']:
			imgFormats=["svg","png"]
			for imgFormat in imgFormats:
				imgFile="{0}.{1}".format(data['icon'],imgFormat)
				self._debug("SEARCH ICON {0}".format(imgFile))
				cmd=[app,"--appimage-extract",imgFile]
				subprocess.run(cmd)
				icn=os.path.join("/tmp","squashfs-root",imgFile)
				if os.path.exists(icn):
					self._debug("Icon found at {}".format(imgFile))
					data['icon']=QIcon(icn)
					break
				else:
					icn=''

		if not icn:
			icn="appimage-manager"
			data['icon']=QIcon.fromTheme(icn)
#		try:
#			shutil.rmtree("/tmp","squashfs-root")
#		except Exception as e:
#			self._debug(e)
		os.chdir(oldDir)
		self._debug("DATA: {}".format(data))
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
