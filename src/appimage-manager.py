#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QStackedWidget,QGridLayout,QTabWidget,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer
import gettext
import subprocess
from app2menu import App2Menu

gettext.textdomain('appimage-manager')
_ = gettext.gettext


RSRC="/usr/share/appimage-manager/rsrc"

class appManager(QWidget):

	def __init__(self,action="",appimage=""):
		super().__init__()
		self.dbg=True
		self._debug("Action %s Appimage %s"%(action,appimage))
		self.height=0
		self._render_gui(action,appimage)
		self.desktop={}
	#def init

	def _debug(self,msg):
		if self.dbg:
			print("Appimage: %s"%msg)
			with open("/tmp/a","a") as f:
				f.write("%s\n"%msg)
	#def _debug

	def _render_gui(self,action="",appimage=""):
		box=QGridLayout()
		tab=QTabWidget()
		tabInstall=self._render_install(action,appimage)
		tab.addTab(tabInstall,_("Install"))
		tabManager=self._render_manager()
		tab.addTab(tabManager,_("Manage"))
		img_banner=QLabel()
		img=QtGui.QPixmap("%s/appimage_banner.png"%RSRC)
		img_banner.setPixmap(img)
		self.statusBar=QStatusBar()
		self.anim=QPropertyAnimation(self.statusBar, b"geometry")
		self.statusBar.hide()
		self.timer=QTimer()
		self.timer.setSingleShot(True)
		box.addWidget(self.statusBar)
		box.addWidget(img_banner)
		box.addWidget(tab)
		self.setLayout(box)
		self.show()

	def _render_manager(self):
		self._debug("Loading manager...")
		tabManager=QWidget()
		tabManager.setStyleSheet(self._managerCss())
		box=QGridLayout()
		row=0
		col=0
		icn_trash=QtGui.QIcon("%s/trash.svg"%RSRC)
		icn_run=QtGui.QIcon("%s/run.svg"%RSRC)
		for app in os.listdir("/usr/local/bin"):
			if app.endswith(".appimage"):
				appBox=QHBoxLayout()
				lbl=QLabel(app)
				btn_remove=QPushButton()
				btn_remove.setIcon(icn_trash)
				btn_remove.setIconSize(QSize(48,48))
				btn_remove.setStyleSheet("""QPushButton{background: red;}""")
				btn_run=QPushButton()
				btn_run.setIcon(icn_run)
				btn_run.setIconSize(QSize(48,48))
				btn_run.setStyleSheet("""QPushButton{background: blue;}""")
				appBox.addWidget(lbl,1,Qt.Alignment(0))
				appBox.addWidget(btn_run,0,Qt.Alignment(2))
				appBox.addWidget(btn_remove,0,Qt.Alignment(2))
				box.addLayout(appBox,row,col)
				row+=1

		tabManager.setLayout(box)
		return(tabManager)
		pass

	def _render_install(self,action="",appimage=""):
		self._debug("Loading installer...")
		tabInstall=QWidget()
		appimage_name=os.path.basename(appimage).rstrip(".appimage")
		desktop={'icon':'x-appimage','name':appimage_name,'comment':'','category':'Other'}
		self.setWindowTitle("Appimage Manager")
		box=QVBoxLayout()
		img_banner=QLabel()
		icn_desktop=QtGui.QIcon.fromTheme("x-appimage")
		btn_desktop=QPushButton(_("Push button to set the icon,\n name and category for the app\n or use default ones"))
		btn_desktop.setIcon(icn_desktop)
		btn_desktop.setIconSize(QSize(64,64))
		btn_desktop.setLayoutDirection(1)
		btn_desktop.clicked.connect(lambda: self._render_desktop_dialog(desktop))
		icn_action=QtGui.QIcon.fromTheme("system-run")
		btn_action=QPushButton(_("%s the application %s")%(action.capitalize(),appimage_name))
		btn_action.setIcon(icn_action)
		btn_action.setIconSize(QSize(64,64))
		btn_action.setLayoutDirection(1)
		btn_action.clicked.connect(lambda: self._install(appimage,desktop))
		box.addWidget(btn_desktop)
		box.addWidget(btn_action)
		self._debug("gui launched")
		tabInstall.setLayout(box)
		return(tabInstall)

	@pyqtSlot()
	def _render_desktop_dialog(self,desktop):
		def _begin_save_desktop():
			name=inp_name.text()
			icon=inp_icon.text()
			comment=inp_desc.text()
			categories=cmb_cat.currentText()
			self._save_desktop_info(name,icon,comment,categories,exe)
			
		dia=QDialog()
		dia.setWindowTitle("Appimage Desktop Definition")
		box=QFormLayout()
		lbl_icon=QLabel(_("Select icon: "))
		inp_icon=QLineEdit(desktop['icon'])
		box.addRow(lbl_icon,inp_icon)
		lbl_name=QLabel(_("Set name: "))
		inp_name=QLineEdit(desktop['name'])
		box.addRow(lbl_name,inp_name)
		lbl_desc=QLabel(_("Set desc: "))
		inp_desc=QLineEdit(desktop['comment'])
		box.addRow(lbl_desc,inp_desc)
		lbl_cat=QLabel(_("Set category: "))
		cmb_cat=QComboBox()
		menu=App2Menu.app2menu()
		categories=menu.get_categories()
		for cat in categories:
			cmb_cat.addItem(cat)
		box.addRow(lbl_cat,cmb_cat)
		icn_apply=QtGui.QIcon.fromTheme("system-run")
		btn_apply=QPushButton(_("Apply"))
		btn_apply.clicked.connect(lambda: _begin_save_desktop(desktop))
		icn_cancel=QtGui.QIcon.fromTheme("system-run")
		btn_cancel=QPushButton(_("Cancel"))
		box.addRow(btn_apply,btn_cancel)
		dia.setLayout(box)
		dia.show()
		dia.exec_()
		return desktop
	#def _render_desktop_dialog

	def _show_message(self,msg):
		def hide_message():
			timer=1000
			self.anim.setDuration(timer)
			self.anim.setStartValue(QRect(0,0,self.width()-10,self.height-10))
			self.anim.setEndValue(QRect(0,0,self.width()-10,0))
			self.anim.start()
			self.timer.singleShot(timer, lambda:self.statusBar.hide())

		self.statusBar.showMessage("%s"%msg)
		self.anim.setDuration(1000)
		self.anim.setLoopCount(1)
		height=self.statusBar.height()/10
		if self.height<height:
			self.height=height
		self.statusBar.show()
		self.anim.setStartValue(QRect(0,0,self.width()-10,0))
		self.anim.setEndValue(QRect(0,0,self.width()-10,self.height-10))
		self.anim.start()
		self.timer.singleShot(3000, lambda:hide_message())

	def _hide_message(self):
		self._debug("Hide")
		timer=1000
		self.anim.setDuration(timer)
		height=self.statusBar.height()/10
		self.anim.setStartValue(QRect(0,0,self.width()-10,height-10))
		self.anim.setEndValue(QRect(0,0,self.width()-10,0))
		self.anim.start()

	def _save_desktop_info(self,name,icon,comment,categories,exe):
		self.desktop['name']=name
		self.desktop['icon']=icon
		self.desktop['comment']=comment
		self.desktop['categories']=categories
		self.desktop['exe']=exe

	@pyqtSlot()
	def _install(self,appimage,desktop):
		
		retval=True
		self._debug("Installing %s"%(appimage))
		dst_path='/usr/local/bin/'
		try:
			(name,icon,comment,categories,exe)=self._generate_desktop(appimage)
			subprocess.check_call(["pkexec","/usr/share/appimage-manager/bin/appimage-helper.py","install",appimage,dst_path,name,icon,comment,categories,exe])
		except Exception as e:
			self._debug(e)
			retval=False
			self._show_message(_("Install Failed"))
		return (retval)
	#def _install

	def _remove(appimage):
		pass
	#def _remove

	def _generate_desktop(self,appimage):
		desktop={}
		desktop=self.desktop.copy()
		desktop['exe']=("/usr/local/bin/%s"%os.path.basename(appimage))
		if not self.desktop:
			desktop['name']=os.path.basename(appimage).rstrip(".appimage")
			desktop['comment']='%s appimage'%desktop['name']
			desktop['icon']='x-appimage'
			desktop['categories']='Utility'
		self._debug("Desktop info loaded")
		return(desktop['name'],desktop['icon'],desktop['comment'],desktop['categories'],desktop['exe'])

	#def _generate_desktop

	def _managerCss(self):
		css="""
		QLabel{
			color:black;
			font=14px Roboto;
			margin: 6px;
			padding:6px;
		}
		"""
		return(css)

def _define_css():
	css="""
	QPushButton{
		padding: 6px;
		margin:6px;
		font: 14px Roboto;
		color:black;
	}
	QPushButton:active{
		padding: 6px;
		margin:6px;
		font: 14px Roboto;
		color:black;
		background:none;
	}
	QStatusBar{
		background:red;
		color:white;
		font: 14px Roboto bold;
	}
	"""
	return(css)
	#def _define_css

#_debug("Init %s"%sys.argv)
err=0
action=""
appimage=""
if len(sys.argv)==2:
	appimage=sys.argv[1]
	#Check if we want to run or install
	if os.path.dirname(appimage)=="/usr/local/bin":
		action="run"
	else:
		action="preinstall"
elif len(sys.argv)==3:
	appimage=sys.argv[2]
	action="install"
#else:
#	_debug("Bad argument %s"%sys.argv)
#	exit(1)
#_debug("Action %s"%action)
#if action=="install":
#	_render_gui(action,appimage)
#elif action=="run":
#	_debug("Executing %s"%appimage)
#	try:
#		subprocess.check_call([appimage])
#	except:
#		try:
#			_render_run(appimage)
##			subprocess.check_call(["pkexec","/usr/share/appimage-manager/bin/appimage-helper.py","run",appimage])
#		except Exception as e:
#			_debug(e)
#			_show_error(e)
#elif action=="preinstall":
#	_render_preinstall(appimage)
#	pass
#exit(0)
app=QApplication([])
print("Action %s"%action)
print("Appimage %s"%appimage)
appimageManager=appManager(action,appimage)
app.instance().setStyleSheet(_define_css())
app.exec_()
