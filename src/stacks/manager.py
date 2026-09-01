#!/usr/bin/python3
import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QGridLayout,QHBoxLayout,QComboBox,QCheckBox,QTableWidget, \
				QGraphicsDropShadowEffect, QHeaderView
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QThread
from QtExtraWidgets import QStackedWindowItem
from stacks.lib.libappmanager import appmanager as appmanager
from app2menu import App2Menu

import gettext
_ = gettext.gettext

i18n={"APP_UNINSTALLED":_("Uninstalled: "),
	"APPLAUNCH":_("Launch"),
	"APPREMOVE":_("Remove"),
	"ERR_NOAPP":_("There're no appimages availables"),
	"MENU":_("Manage"),
	"MENU_DESC":_("Manage appimages"),
	"MENU_TOOLTIP":_("Manage installed appimages"),
	}

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

class appWidget(QWidget):
	remove=Signal("PyObject")
	execute=Signal("PyObject")
	def __init__(self,appimage,parent=None):
		super (appWidget,self).__init__(parent)
		self.desktop=''
		self.app=appimage
		self.exeApp=exeApp()
		self.exeApp.finished.connect(self._endExecuteApp)
		self.__initScreen__()
	#def __init__

	def __initScreen__(self,*args):
		fontBtn=self.font()
		fontBtn.setPointSize(fontBtn.pointSize()-2)
		box=QGridLayout()
		box.setColumnStretch(0,-1)
		box.setColumnStretch(1,1)
		self.btnIcon=QPushButton()
		effect=QGraphicsDropShadowEffect(blurRadius=5,xOffset=3,yOffset=3)
		self.btnIcon.setGraphicsEffect(effect)
		self.btnIcon.setIconSize(QSize(64,64))
		self.btnIcon.setMinimumHeight(72)
		#self.btnIcon.clicked.connect(self._executeApp)
		box.addWidget(self.btnIcon,0,0,2,1,Qt.AlignLeft)
		self.lblName=QLabel("")
		self.lblName.setObjectName("appName")
		box.addWidget(self.lblName,0,1,1,1,Qt.AlignLeft)
		self.lblDesc=QLabel("")
		box.addWidget(self.lblDesc,1,1,1,3,Qt.AlignLeft)
		self.btnLaunch=QPushButton(i18n["APPLAUNCH"])
		self.btnLaunch.setFont(fontBtn)
		self.btnLaunch.setObjectName("btnLaunch")
		self.btnLaunch.clicked.connect(self._executeApp)
		self.btnLaunch.setCursor(Qt.PointingHandCursor)
		box.addWidget(self.btnLaunch,0,2,1,1,Qt.AlignLeft)
		self.btnRemove=QPushButton(i18n["APPREMOVE"])
		self.btnRemove.setFont(fontBtn)
		self.btnRemove.setObjectName("btnRemove")
		self.btnRemove.clicked.connect(self._removeApp)
		self.btnRemove.setCursor(Qt.PointingHandCursor)
		box.addWidget(self.btnRemove,0,3,1,1,Qt.AlignLeft)
		self.setObjectName("cell")
		self.setLayout(box)
		self.setStyleSheet(self._setCss())
	#def __initScreen__

	def mouseDoubleClickEvent(self,*args):
		self._executeApp()
	#def mouseDoubleClickEvent

	def getApp(self):
		return(self.app)

	def setIcon(self,icon):
		self.btnIcon.setIcon(icon)
	#def setIcon

	def setName(self,name):
		self.lblName.setText(name)
	#def setName

	def getName(self):
		return(self.lblName.text())
	#def getName

	def setDesc(self,desc):
		self.lblDesc.setText(desc)
	#def setDesc
	
	def setExe(self,exe):
		self.exe=exe.replace("'","")
	#def setExe

	def _removeApp(self):
		self.remove.emit(self)
	#def _removeApp

	def _executeApp(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.btnLaunch.setCursor(cursor)
		cursor=QtGui.QCursor(Qt.ForbiddenCursor)
		self.btnRemove.setCursor(cursor)
		self.blockSignals(True)
		self.exeApp.setApp(self.app)
		self.exeApp.start()
	#def _executeApp(self):

	def _endExecuteApp(self):
		cursor=QtGui.QCursor(Qt.PointingHandCursor)
		self.btnLaunch.setCursor(cursor)
		self.btnRemove.setCursor(cursor)
		self.blockSignals(False)
	#def _endExecuteApp

	def _setCss(self):
		css="""
		#btnRemove{
			background:red;
			color:white;
		}
		"""
	#def _setCss

#class appWidget

class manager(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("manager load")
		self.setProps(shortDesc=i18n["MENU"],
			longDesc=i18n["MENU_DESC"],
			icon="systemsettings",
			tooltip=_("Add custom repositories"),
			index=1,
			visible=True)
		self.hideControlButtons()
		self.appmanager=appmanager()
		self.menu=App2Menu.app2menu()
		self.lstAppimage=QTableWidget(0,1)
		self.setStyleSheet(self._setCss())
		self.widget=''
		self.paths=[os.path.join(os.environ["HOME"],"Applications"),
					os.path.join(os.environ["HOME"],"AppImages"),
					os.path.join(os.environ["HOME"],"Appimages"),
					os.path.join(os.environ["HOME"],".local","bin"),
					"/usr/local/bin"]
	#def __init__
	
	def __initScreen__(self):
		box=QVBoxLayout()
		self.lstAppimage.setShowGrid(False)
		self.lstAppimage.horizontalHeader().hide()
		self.lstAppimage.verticalHeader().hide()
		self.lstAppimage.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.lstAppimage.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		box.addWidget(self.lstAppimage)
		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def updateScreen(self):
		self.lstAppimage.setRowCount(0)
		for path in self.paths:
			if os.path.isdir(path):
				for f in os.scandir(path):
					if f.name.lower().endswith(".appimage"):
						appCell=self._paintCell(f.path)
						if appCell:
							self.lstAppimage.setRowCount(self.lstAppimage.rowCount()+1)
							self.lstAppimage.setCellWidget(self.lstAppimage.rowCount()-1,0,appCell)
							self.lstAppimage.resizeRowToContents(self.lstAppimage.rowCount()-1)
		if self.lstAppimage.rowCount()==0:
			self.lstAppimage.insertRow(0)
			lbl=QLabel(i18n["ERR_NOAPP"])
			lbl.setStyleSheet("background:silver;border:0px;margin:0px")
			self.lstAppimage.setCellWidget(0,0,lbl)

		self.lstAppimage.resizeColumnsToContents()

		return True
	#def _udpate_screen

	def _paintCell(self,appimage):
		widget=None
		if appimage:
			data=self.appmanager.getAppData(appimage)
			if data.get('name',''):
				widget=appWidget(appimage)
				widget.remove.connect(self._removeApp)
				widget.setName(data['name'])
#				icon=desktop.get('Icon','')
				widget.setIcon(data['icon'])
				widget.setDesc(data['desc'])
				widget.setExe(data['exe'])
		return widget
	#def _paintCell

	def writeConfig(self):
		if self.widget=='':
			return
		self.appmanager.localRemove(self.widget.getApp())
		self.showMsg("{0} {1}".format(i18n ["APP_UNINSTALLED"],self.widget.getName()))
		self.updateScreen()
	#def writeConfig

	def _removeApp(self,widget):
		self.widget=widget
		self.writeConfig()
	#def _removeApp

	def _setCss(self):
		css="""
		#cell{
			padding:10px;
			margin:6px;
			background-color:rgb(250,250,250);

		}
		#appName{
			font-weight:bold;
			border:0px;
		}
		#btnRemove{
			background:red;
			color:white;
			padding:3px;
			margin:3px;
		}
		
		"""

		return(css)
	#def _setCss

