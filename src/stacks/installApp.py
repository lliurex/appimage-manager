#!/usr/bin/python3
import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QGridLayout,QHBoxLayout,QComboBox,QCheckBox, QListWidget,QFileDialog,QFrame
from PyQt5 import QtGui
from PyQt5.QtCore import Qt,QSize
from appconfig.appConfigStack import appConfigStack as confStack
from edupals.ui import QAnimatedStatusBar
import airmanager.airmanager as installer
import tempfile
from gi.repository import GdkPixbuf

import gettext
_ = gettext.gettext

class installApp(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("installer load")
		self.description=(_("Appimage Installer"))
		self.menu_description=(_("Install appimages"))
		self.icon=('x-appimage')
		self.tooltip=(_("From here you can install appimages on your system"))
		self.index=2
		self.enabled=True
		self.level='system'
#		self.hideControlButtons()
		self.airinstaller=installer.AirManager()	
		self.setStyleSheet(self._setCss())
	#def __init__
	
	def _load_screen(self):

		def _fileChooser():
			fdia=QFileDialog()
			fdia.setNameFilter("appimages(*.appimage)")
			if (fdia.exec_()):
				fchoosed=fdia.selectedFiles()[0]
				self.inp_file.setText(fchoosed)
				self.updateScreen()
		box=QGridLayout()
		box.addWidget(QLabel(_("Appimage")),0,0,1,1,Qt.AlignBottom)
		self.inp_file=QLineEdit()
		self.inp_file.setPlaceholderText(_("Choose file for install"))
		box.addWidget(self.inp_file,1,0,1,1,Qt.AlignTop)
		btn_file=QPushButton("...")
		btn_file.setObjectName("fileButton")
		btn_file.clicked.connect(_fileChooser)
		box.addWidget(btn_file,1,1,1,1,Qt.AlignLeft|Qt.AlignTop)
		self.frame=QFrame()
		box.addWidget(self.frame,2,0,1,1,Qt.AlignTop)
		framebox=QGridLayout()
		self.frame.setLayout(framebox)
		framebox.addWidget(QLabel(_("App name")),0,0,1,1,Qt.AlignBottom)
		self.btn_icon=QPushButton()
		self.btn_icon.setToolTip(_("Push for icon change"))
		framebox.addWidget(self.btn_icon,0,1,2,1,Qt.AlignLeft)
		self.inp_name=QLineEdit()
		self.inp_name.setObjectName("fileInput")
		self.inp_name.setPlaceholderText(_("Application name"))
		framebox.addWidget(self.inp_name,1,0,1,1,Qt.AlignTop)
		framebox.addWidget(QLabel(_("App description")),2,0,1,1,Qt.AlignBottom)
		self.inp_desc=QLineEdit()
		self.inp_desc.setPlaceholderText(_("Application description"))
		framebox.addWidget(self.inp_desc,3,0,1,2,Qt.AlignTop)
		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def _loadAppData(self,app=""):
		if app:
			icon=""
			subprocess.run(["chmod","+x","%s"%app])
			output=subprocess.check_output(["%s"%app,"--appimage-extract","*.desktop"])
			output=output.decode("utf-8")
			with open(output.replace("\n",""),'r') as f:
				for line in f.readlines():
					if line.startswith("Exec"):
						exe=line.split("=")[-1]
					if line.startswith("Name="):
						name=line.split("=")[-1]
					if line.startswith("Icon"):
						icon=line.split("=")[-1].strip()
					if line.startswith("Comment="):
						desc=line.split("=")[-1]
			if icon:
				output=subprocess.check_output(["%s"%app,"--appimage-extract","%s.svg"%icon])
				if not output:
					output=subprocess.check_output(["%s"%app,"--appimage-extract","%s.png"%icon])
				if output:
					icn=output.decode("utf-8").replace("\n","")
					print(icn)
					icon=QtGui.QIcon("./%s"%icn)

			if not icon:
				icon="x-appimage"
				icon=QtGui.QIcon.fromTheme(icon)
			self.inp_name.setText(name)
			self.inp_desc.setText(desc)
			self.btn_icon.setIcon(icon)
		else:
			self.inp_name.setText("")
			self.inp_desc.setText("")
			icon=QtGui.QIcon.fromTheme("x-appimage")
			self.btn_icon.setIcon(icon)
			self.btn_icon.setIconSize(QSize(64,64))
			self.frame.setEnabled(False)
	#def _loadAppData

	def updateScreen(self):
		self.frame.setEnabled(True)
		app=self.inp_file.text()
		self._loadAppData(app)
		return True
	#def _udpate_screen
	
	def writeConfig(self):
		tmp_icon=tempfile.mkstemp()[1]
		self.btn_icon.icon().pixmap(QSize(64,64)).save(tmp_icon,"PNG")
		subprocess.check_call(['/usr/bin/xhost','+'])
		air=self.inp_file.text()
		try:
			ins=subprocess.check_call(['pkexec','/usr/bin/air-helper-installer.py','install',air,tmp_icon])
			self.install_err=False
		except Exception as e:
			self._debug(e)
		subprocess.check_output(["xdg-mime","install","/usr/share/mime/packages/x-air-installer.xml"])
		subprocess.check_output(["xdg-mime","default","/usr/share/applications/air-installer.desktop","/usr/share/mime/packages/x-air-installer.xml"],input=b"")
		subprocess.check_call(['/usr/bin/xhost','-'])
		self.showMsg(_("App %s installed succesfully"%os.path.basename(air)))
	#def writeConfig

	def _setCss(self):
		css="""
			#fileButton{
				margin:0px;
				padding:1px;
			}
			#fileInput{
				margin:0px;
			}
			#imgButton{
				margin:0px;
				padding:0px;
			}"""
		return(css)
	#def _setCss

