#!/usr/bin/python3
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QGridLayout,QHBoxLayout,QComboBox,QCheckBox, QListWidget,QFileDialog,QFrame
from PyQt5 import QtGui
from PyQt5.QtCore import Qt,QSize
from appconfig.appConfigStack import appConfigStack as confStack
from stacks.lib.libappmanager import appmanager as appmanager

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
		self.setStyleSheet(self._setCss())
		self.appPath="%s/Applications"%os.environ["HOME"]
		self.appmanager=appmanager()
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
			data=self.appmanager.getAppData(app)
			self.inp_name.setText(data.get('name',''))
			self.inp_desc.setText(data.get('desc',''))
			self.btn_icon.setIcon(data.get('icon',''))
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
		app=self.inp_file.text()
		if self.appmanager.localInstall(app):
			self.showMsg(_("App %s installed succesfully"%os.path.basename(app)))
		else:
			self.showMsg(_("App %s could not be installed"%os.path.basename(app)))
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
