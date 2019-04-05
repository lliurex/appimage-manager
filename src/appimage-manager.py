#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QStackedWidget,QGridLayout,QTabWidget,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal
import gettext
import subprocess
from app2menu import App2Menu

gettext.textdomain('appimage-manager')
_ = gettext.gettext


RSRC="/usr/share/appimage-manager/rsrc"

class th_getCategories(QThread):
	signal=pyqtSignal("PyQt_PyObject")
	def __init__(self):
		QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		menu=App2Menu.app2menu()
		categories=menu.get_categories()
		self.signal.emit(categories)

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
		appimage_name=os.path.basename(appimage).rstrip(".appimage")
		desktop={'icon':'x-appimage','name':appimage_name,'comment':'','categories':'Utility'}
		def _begin_render_desktop(f_desktop):
			nonlocal desktop
			(f_desktop,status)=self._render_desktop_dialog(f_desktop)
			desktop=f_desktop
			if desktop['icon']:
				if os.path.isfile(desktop['icon']):
					icn=QtGui.QIcon(desktop['icon'])
				else:
					icn=QtGui.QIcon.fromTheme(desktop['icon'])
				img_desktop.setPixmap(icn.pixmap(QSize(64,64)))
			else:
				desktop['icon']='x-appimage'
			print("D: %s"%desktop)
#			btn_action.disconnect()
#			btn_action.clicked.connect(lambda: self._install(appimage,desktop))

		self._debug("Loading installer...")
		tabInstall=QWidget()
		self.setWindowTitle("Appimage Manager")
		box=QVBoxLayout()
		deskbox=QHBoxLayout()
		btn_desktop=QPushButton("")
		btn_desktop.setObjectName("menuButton")
		lbl_desktop=QLabel(_("Push button to set the icon,\n name and category for the app\n or use default ones"))
		deskbox.addWidget(lbl_desktop,1,Qt.Alignment(0))
		icn_desktop=QtGui.QIcon.fromTheme("x-appimage")
		img_desktop=QLabel()
		img_desktop.setPixmap(icn_desktop.pixmap(QSize(64,64)))
		deskbox.addWidget(img_desktop,0,Qt.Alignment(2))
		btn_desktop.setLayout(deskbox)
		btn_desktop.clicked.connect(lambda: _begin_render_desktop(desktop))
		actionbox=QHBoxLayout()
		btn_action=QPushButton("")
		btn_action.setObjectName("menuButton")
		lbl_action=QLabel(_("%s the application %s")%(action.capitalize(),appimage_name))
		actionbox.addWidget(lbl_action,1,Qt.Alignment(0))
		icn_action=QtGui.QIcon.fromTheme("system-run")
		img_action=QLabel()
		img_action.setPixmap(icn_action.pixmap(QSize(64,64)))
		actionbox.addWidget(img_action,0,Qt.Alignment(2))
		btn_action.setLayout(actionbox)
		btn_action.clicked.connect(lambda: self._install(appimage,desktop))
		box.addWidget(btn_desktop)
		box.addWidget(btn_action)
		self._debug("gui launched")
		tabInstall.setLayout(box)
		return(tabInstall)

	@pyqtSlot()
	def _render_desktop_dialog(self,desktop):
		categories=[]
		fdia=QFileDialog()
		icon="x-appimage"
		def _file_chooser():
			fdia.setFileMode(QFileDialog.AnyFile)
			fdia.setNameFilter(_("images(*.png *.xpm *jpg)"))
			if (fdia.exec_()):
				icon=fdia.selectedFiles()[0]
				icn=QtGui.QIcon(icon)
				btn_icon.setIcon(icn)

		def _begin_save_desktop():
			name=inp_name.text()
			comment=inp_desc.text()
			categories=cmb_cat.currentText()
			desktop['name']=name
			if fdia.selectedFiles():
				icon=fdia.selectedFiles()[0]
			else:
				icon='x-appimage'
			desktop['icon']=icon
			desktop['comment']=comment
			desktop['categories']=categories
			dia.accept()
			
		def _set_categories(categories):
			filter_categories=['debian','help']
			for cat in categories:
				if cat and cat not in filter_categories:
					cmb_cat.addItem(_(cat))
			cmb_cat.adjustSize()
		dia=QDialog()
		dia.setWindowTitle("Appimage Desktop Definition")
		box=QFormLayout()
		lbl_icon=QLabel(_("Select icon: "))
		inp_icon=QLineEdit(desktop['icon'])
		btn_icon=QPushButton()
		icn_desktop=QtGui.QIcon.fromTheme(icon)
		btn_icon.setIcon(icn_desktop)
		btn_icon.setIconSize(QSize(64,64))
		btn_icon.clicked.connect(_file_chooser)
		box.addRow(lbl_icon,btn_icon)
		lbl_name=QLabel(_("Set name: "))
		inp_name=QLineEdit(desktop['name'])
		box.addRow(lbl_name,inp_name)
		lbl_desc=QLabel(_("Set desc: "))
		inp_desc=QLineEdit(desktop['comment'])
		box.addRow(lbl_desc,inp_desc)
		lbl_cat=QLabel(_("Set category: "))
		cmb_cat=QComboBox()
		cmb_cat.setSizeAdjustPolicy(0)
		th_categories=th_getCategories()
		th_categories.start()
		th_categories.signal.connect(_set_categories)
		box.addRow(lbl_cat,cmb_cat)
		btnBox=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
		btnBox.rejected.connect(dia.reject)
		btnBox.accepted.connect(_begin_save_desktop)
#		box.addRow(btn_apply,btn_cancel)
		box.addRow(btnBox)
		dia.setLayout(box)
		dia.show()
		result=dia.exec_()
		return (desktop,result==QDialog.Accepted)
	#def _render_desktop_dialog

	def _show_message(self,msg,css=None):
		def hide_message():
			timer=1000
			self.anim.setDuration(timer)
			self.anim.setStartValue(QRect(0,0,self.width()-10,self.height-10))
			self.anim.setEndValue(QRect(0,0,self.width()-10,0))
			self.anim.start()
			self.timer.singleShot(timer, lambda:self.statusBar.hide())
		if css:
			self.statusBar.setStyleSheet("""QStatusBar{%s;}"""%css)
		else:
			self.statusBar.setStyleSheet("""QStatusBar{background:red;}""")
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

	@pyqtSlot()
	def _install(self,appimage,desktop):
		
		retval=True
		self._debug("Installing %s"%(appimage))
		dst_path='/usr/local/bin/'
		try:
			(name,icon,comment,categories,exe)=self._generate_desktop(appimage,desktop)
			subprocess.check_call(["pkexec","/usr/share/appimage-manager/bin/appimage-helper.py","install",appimage,dst_path,name,icon,comment,categories,exe])
			self._show_message(_("%s installed"%name),"background:blue")
		except Exception as e:
			self._debug(e)
			retval=False
			self._show_message(_("Install Failed"))
		return (retval)
	#def _install

	def _remove(appimage):
		pass
	#def _remove

	def _generate_desktop(self,appimage,desktop):
		desktop['exe']=("/usr/local/bin/%s"%os.path.basename(appimage))
		if 'name' not in desktop.keys() or not desktop['name']:
			desktop['name']=os.path.basename(appimage).rstrip(".appimage")
		if 'comment' not in desktop.keys() or not desktop['comment']:
			desktop['comment']='%s appimage'%desktop['name']
		if 'icon' not in desktop.keys() or not desktop['icon']:
			desktop['icon']='x-appimage'
		if 'categories' not in desktop.keys() or not desktop['categories']:
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
	QPushButton#menuButton{
		height:72px;
	}
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
	QLabel{
		padding:6px;
		margin:6px;
	}
	"""
	return(css)
	#def _define_css

#_debug("Init %s"%sys.argv)
err=0
action=""
appimage=""
print(sys.argv)
if len(sys.argv)==2:
	appimage=sys.argv[1]
	action="run"
elif len(sys.argv)==3:
	appimage=sys.argv[2]
	action="install"
else:
	exit(1)
if action=="install":
	app=QApplication([])
	appimageManager=appManager(action,appimage)
	app.instance().setStyleSheet(_define_css())
	app.exec_()
elif action=="run":
	try:
		os.chmod(appimage,0o755)
		subprocess.check_call([appimage])
	except:
		try:
			subprocess.check_call(["pkexec","/usr/share/appimage-manager/bin/appimage-helper.py","run",appimage])
		except Exception as e:
			print(e)
