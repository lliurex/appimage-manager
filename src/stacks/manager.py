#!/usr/bin/python3
import sys
import os
import subprocess
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QGridLayout,QHBoxLayout,QComboBox,QCheckBox,QTableWidget, \
				QGraphicsDropShadowEffect, QHeaderView
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize,Signal
from QtExtraWidgets import QStackedWindowItem
from stacks.lib.libappmanager import appmanager as appmanager
from app2menu import App2Menu

import gettext
_ = gettext.gettext

i18n={"APP_UNINSTALLED":_("Uninstalled: "),
	"BTN_REMOVE":_("Remove"),
	"ERR_NOAPP":_("There're no appimages availables"),
	"MENU":_("Appimage Manager"),
	"MENU_DESC":_("Manage appimages"),
	"MENU_TOOLTIP":_("From here you can manage the appimage availables on your system"),
	}

class appWidget(QWidget):
	remove=Signal("PyObject")
	execute=Signal("PyObject")
	def __init__(self,appimage,parent=None):
		super (appWidget,self).__init__(parent)
		self.desktop=''
		self.app=appimage
		box=QGridLayout()
		box.setColumnStretch(0,-1)
		box.setColumnStretch(1,1)
		self.btn_icon=QPushButton()
		effect=QGraphicsDropShadowEffect(blurRadius=5,xOffset=3,yOffset=3)
		self.btn_icon.setGraphicsEffect(effect)
		self.btn_icon.setIconSize(QSize(64,64))
		self.btn_icon.setMinimumHeight(72)
		self.btn_icon.clicked.connect(self._executeAir)
		box.addWidget(self.btn_icon,0,0,2,1,Qt.AlignLeft)
		self.lbl_name=QLabel("")
		self.lbl_name.setObjectName("appName")
		box.addWidget(self.lbl_name,0,1,1,1,Qt.AlignLeft)
		self.lbl_desc=QLabel("")
		box.addWidget(self.lbl_desc,1,1,1,2,Qt.AlignLeft)
		btn_remove=QPushButton(i18n["BTN_REMOVE"])
		btn_remove.setObjectName("btnRemove")
		btn_remove.clicked.connect(self._removeAir)
		box.addWidget(btn_remove,0,2,1,1,Qt.AlignLeft)
		self.setObjectName("cell")
		self.setLayout(box)
		self.setStyleSheet(self._setCss())
	#def __init__

	def mouseDoubleClickEvent(self,*args):
		self._executeAir()

	def getApp(self):
		return(self.app)

	def setIcon(self,icon):
		self.btn_icon.setIcon(icon)
	#def setIcon

	def setDesktop(self,desktop):
		self.desktop=desktop
	#def setName

	def getDesktop(self):
		return(self.desktop)

	def setName(self,name):
		self.lbl_name.setText(name)
	#def setName

	def getName(self):
		return(self.lbl_name.text())

	def setDesc(self,desc):
		self.lbl_desc.setText(desc)
	#def setDesc
	
	def getDesc(self):
		return(self.lbl_desc.text())
	
	def getIcon(self):
		return(self.lbl_desc.text())
	
	def setExe(self,exe):
		self.exe=exe.replace("'","")
	#def setExe

	def _removeAir(self):
		self.remove.emit(self)

	def _executeAir(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.pid=subprocess.Popen(self.app,stdin=None,stdout=None,stderr=None,shell=False)
		cursor=QtGui.QCursor(Qt.ArrowCursor)
		self.setCursor(cursor)
	#def _executeAir(self):

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
			font-size:9pt;
			padding:3px;
			margin:3px;
		}"""
	#def _setCss

#class airWidget

class manager(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("manager load")
		self.setProps(shortDesc=i18n["MENU"],
			longDesc=i18n["MENU_DESC"],
			icon="document-new",
			tooltip=_("Add custom repositories"),
			index=1,
			visible=True)
		self.hideControlButtons()
		self.appmanager=appmanager()
		self.menu=App2Menu.app2menu()
		self.lst_appimage=QTableWidget(0,1)
		self.setStyleSheet(self._setCss())
		self.widget=''
		self.paths=["/usr/local/bin",
					os.path.join(os.environ["HOME"],"AppImages"),
					os.path.join(os.environ["HOME"],"Applications")]
	#def __init__
	
	def __initScreen__(self):
		box=QVBoxLayout()
		self.lst_appimage.setShowGrid(False)
		self.lst_appimage.horizontalHeader().hide()
		self.lst_appimage.verticalHeader().hide()
		self.lst_appimage.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.lst_appimage.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		box.addWidget(self.lst_appimage)
		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def updateScreen(self):
		self.lst_appimage.clear()
		cont=0
		for path in self.paths:
			if os.path.isdir(path):
				for fn in os.listdir(path):
					if fn.endswith("appimage"):
						appCell=self._paintCell(os.path.join(path,fn))
						if appCell:
							self.lst_appimage.insertRow(cont)
							self.lst_appimage.setCellWidget(cont,0,appCell)
							self.lst_appimage.resizeRowToContents(cont)
							cont+=1
		if cont==0:
			self.lst_appimage.insertRow(0)
			lbl=QLabel(i18n["ERR_NOAPP"])
			lbl.setStyleSheet("background:silver;border:0px;margin:0px")
			self.lst_appimage.setCellWidget(0,0,lbl)
			cont+=1

		while (cont<self.lst_appimage.rowCount()):
			self.lst_appimage.removeRow(cont)
		self.lst_appimage.resizeColumnsToContents()

		return True
	#def _udpate_screen

	def _paintCell(self,appimage):
		widget=None
		if appimage:
			data=self.appmanager.getAppData(appimage)
			if data.get('name',''):
				widget=appWidget(appimage)
#				widget.setDesktop(airApp.get('desktop'))
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
	#def _removeAir

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
			font-size:9pt;
			padding:3px;
			margin:3px;
		}
		
		"""

		return(css)
	#def _setCss

