#!/usr/bin/python3
import os
import subprocess
from PySide2.QtWidgets import QLabel, QGridLayout,QTableWidget,QHeaderView
from PySide2.QtCore import Qt,QThread
from QtExtraWidgets import QStackedWindowItem
from stacks.lib.libappmanager import appmanager as appmanager
from wdg.appWidget import appWidget
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
		box=QGridLayout()
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

