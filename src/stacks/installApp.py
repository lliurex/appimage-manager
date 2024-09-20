#!/usr/bin/python3
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QGridLayout,QHBoxLayout,QComboBox,QCheckBox, QListWidget,QFileDialog,QFrame
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize
from QtExtraWidgets import QStackedWindowItem
from stacks.lib.libappmanager import appmanager as appmanager

import gettext
_ = gettext.gettext

i18n={"APP_ADD":_("Choose appimage to add"),
	"APP_DESC":_("Application description"),
	"APP_NAME":_("Appication name"),
	"BTN_ICON_TOOLTIP":_("Push for icon change"),
	"INSTALL_OK":_("Installed"),
	"INSTALL_KO":_("Install failed: "),
	"MENU":_("Add Appimage"),
	"MENU_DESC":_("Add appimages"),
	"MENU_TOOLTIP":_("From here you can add an appimages from your system"),
	}
class installApp(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("addApp load")
		self.setProps(shortDesc=i18n["MENU"],
			longDesc=i18n["MENU_DESC"],
			icon="document-new",
			tooltip=i18n["MENU_TOOLTIP"],
			index=2,
			visible=True)
		self.setStyleSheet(self._setCss())
		self.appPath=os.path.join(os.environ["HOME"],"Applications")
		self.appmanager=appmanager()
	#def __init__
	
	def _fileChooser(self):
		fdia=QFileDialog()
		fdia.setNameFilter("appimages(*.appimage)")
		if (fdia.exec_()):
			fchoosed=fdia.selectedFiles()[0]
			self.inp_file.setText(fchoosed)
			self.updateScreen()
	#def _fileChooser

	def __initScreen__(self):
		box=QGridLayout()
		box.addWidget(QLabel("Appimage"),0,0,1,1,Qt.AlignBottom)
		self.inp_file=QLineEdit()
		self.inp_file.setPlaceholderText(i18n["APP_ADD"])
		box.addWidget(self.inp_file,1,0,1,1,Qt.AlignTop)
		btn_file=QPushButton("...")
		btn_file.setObjectName("fileButton")
		btn_file.clicked.connect(self._fileChooser)
		box.addWidget(btn_file,1,1,1,1,Qt.AlignLeft|Qt.AlignTop)
		self.frame=QFrame()
		box.addWidget(self.frame,2,0,1,1,Qt.AlignTop)
		framebox=QGridLayout()
		self.frame.setLayout(framebox)
		framebox.addWidget(QLabel(i18n["APP_NAME"]),0,0,1,1,Qt.AlignBottom)
		self.btn_icon=QPushButton()
		self.btn_icon.setToolTip(i18n["BTN_ICON_TOOLTIP"])
		framebox.addWidget(self.btn_icon,0,1,2,1,Qt.AlignLeft)
		self.inp_name=QLineEdit()
		self.inp_name.setObjectName("fileInput")
		self.inp_name.setPlaceholderText(i18n["APP_NAME"])
		framebox.addWidget(self.inp_name,1,0,1,1,Qt.AlignTop)
		framebox.addWidget(QLabel(i18n["APP_DESC"]),2,0,1,1,Qt.AlignBottom)
		self.inp_desc=QLineEdit()
		self.inp_desc.setPlaceholderText(i18n["APP_DESC"])
		framebox.addWidget(self.inp_desc,3,0,1,2,Qt.AlignTop)
		self.setLayout(box)
		return(self)
	#def __initScreen__

	def _loadAppData(self,app=""):
		if app:
			data=self.appmanager.getAppData(app)
			self.inp_name.setText(data.get('name',''))
			self.inp_desc.setText(data.get('desc',''))
			self.btn_icon.setIcon(data.get('icon',''))
		else:
			self.inp_name.setText("")
			self.inp_desc.setText("")
			icon=QtGui.QIcon.fromTheme("appimage-manager")
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
			self.showMsg("{0}: {1}".format(i18n["INSTALL_OK"],os.path.basename(app)))
		else:
			self.showMsg("{0}: {1}".format(i18n["INSTALL_KO"],os.path.basename(app)))
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
