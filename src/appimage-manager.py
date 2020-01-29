#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QStackedWidget,QGridLayout,QTabWidget,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QCheckBox,QTableWidget,\
				QTableWidgetItem,QHeaderView,QTableWidgetSelectionRange
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper
import gettext
import subprocess
from app2menu import App2Menu
from edupals.ui import QAnimatedStatusBar
QString=type("")

gettext.textdomain('appimage-manager')
_ = gettext.gettext


RSRC="/usr/share/appimage-manager/rsrc"

class th_runApp(QThread):
	signal=pyqtSignal("PyQt_PyObject")
	def __init__(self,appimage,parent=None):
		QThread.__init__(self,parent)
		self.appimage=appimage

	def __del__(self):
		self.wait()
		pass

	def run(self):
		retval=False
		print("Launching thread...")
		try:
			subprocess.Popen([self.appimage],stdin=None,stdout=None,stderr=None,shell=False)
			retval=True
		except Exception as e:
			print("Error running: %s"%e)
			try:
				subprocess.Popen(["pkexec","/usr/share/appimage-manager/bin/appimage-helper.py","run",self.appimage],shell=False)
				retval=True
			except Exception as e:
				retval=False
				print("Error pkexec: %s"%e)
		self.signal.emit(retval)

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

	update_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self,action="",appimage=""):
		super().__init__()
		self.dbg=False
		self.setWindowIcon(QtGui.QIcon("/usr/share/icons/hicolor/48x48/apps/x-appimage.png"))
		self._debug("Action %s Appimage %s"%(action,appimage))
		self.paths=["/usr/local/bin","%s/AppImages"%os.environ["HOME"],"%s/Applications"%os.environ["HOME"]]
		self.height=0
		#Prevent appimage desktop integration
		if not os.path.isfile("%s/.local/share/appimagekit/no_desktopintegration"%os.environ['HOME']):
			try:
				os.makedirs("%s/.local/share/appimagekit/"%os.environ['HOME'])
			except:
				pass
			f=open("%s/.local/share/appimagekit/no_desktopintegration"%os.environ['HOME'],'w')
			f.close()
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
		self.tab=QTabWidget()
#		if action=="manage":
		tabManager=self._render_manager()
		self.tab.insertTab(0,tabManager,_("Manage"))
		tabInstall=self._render_install(action,appimage)
		self.tab.insertTab(1,tabInstall,_("Install"))
		img_banner=QLabel()
		img=QtGui.QPixmap("%s/appimage_banner.png"%RSRC)
		img_banner.setPixmap(img)
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.statusBar.setStateCss("success","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(0,0,255,1), stop:1 rgba(0,0,255,0.6));color:white;")
		box.addWidget(self.statusBar,0,0,1,1)
		box.addWidget(img_banner,0,0,1,1)
		box.addWidget(self.tab,1,0,1,1)
		self.setLayout(box)
		if action=="install":
			self.tab.setCurrentIndex(1)
		self.show()

	def _render_manager(self):
		def _begin_remove(appimage):
			self._debug("Removing %s"%(appimage))
			if self._remove_appimage(appimage):
				self._show_message(_("Removed %s"%appimage),"success")
				_reload_grid(box)
			else:
				self._show_message(_("Error removing %s"%appimage))
		def _begin_run(appimage):
			self._debug("Executing %s"%appimage)
			self._run_appimage(appimage)

		def _begin_install(appimage):
			self._debug("Installing %s"%appimage)
			self.tab.removeTab(1)
			tabInstall=self._render_install("install",appimage)
			self.tab.insertTab(1,tabInstall,_("Install"))
			self.tab.setCurrentIndex(1)

		def _reload_grid(box):
			paths=[]
			if chk_local.isChecked():
				paths.append("%s/Applications"%os.environ['HOME'])
			if chk_system.isChecked():
				paths.append("/usr/local/bin")
			(box,sigmap_run,sigmap_remove,sigmap_install)=self._load_appimages(paths,box)
			sigmap_run.mapped[QString].connect(_begin_run)
			sigmap_remove.mapped[QString].connect(_begin_remove)
			sigmap_install.mapped[QString].connect(_begin_install)
		self._debug("Loading manager...")
		tabManager=QWidget()
		scrollArea=QScrollArea(tabManager)
		scrollArea.setGeometry(QRect(0,0,620,245))
		tabManager.setStyleSheet(self._managerCss())
		chkBox=QHBoxLayout()
		chk_system=QCheckBox(_("Show system apps"))
		chk_system.setChecked(True)
		chk_local=QCheckBox(_("Show local apps"))
		chk_local.setChecked(True)
		chkBox.addWidget(chk_system)
		chkBox.addWidget(chk_local)

		tabScrolled=QWidget()
		tabScrolled.setObjectName("scrollbox")
		scrollArea.setObjectName("scrollbox")
		(box,sigmap_run,sigmap_remove,sigmap_install)=self._load_appimages(self.paths)
		chk_system.stateChanged.connect(lambda:_reload_grid(box))
		chk_local.stateChanged.connect(lambda:_reload_grid(box))
		sigmap_run.mapped[QString].connect(_begin_run)
		sigmap_remove.mapped[QString].connect(_begin_remove)
		sigmap_install.mapped[QString].connect(_begin_install)
		vbox=QGridLayout()
		vbox.addWidget(chk_local,0,Qt.Alignment(0))
		vbox.addWidget(chk_system,0,Qt.Alignment(1))
		vbox.addWidget(box,1,0,1,2)
		tabScrolled.setLayout(vbox)
		scrollArea.setWidget(tabScrolled)
		scrollArea.alignment()
		scrollArea.setWidgetResizable(True)
		s=self.update_signal
		self.update_signal.connect(lambda:_reload_grid(box))
		return(tabManager)

	def _load_appimages(self,paths=[],box=None):
		row=0
		col=4
#		icn_trash=QtGui.QIcon("%s/trash.svg"%RSRC)
		icn_trash=QtGui.QIcon.fromTheme("application-exit")
#		icn_run=QtGui.QIcon("%s/run.svg"%RSRC)
		icn_run=QtGui.QIcon.fromTheme("system-run")
		icn_install=QtGui.QIcon.fromTheme("system-software-install")
		if box:
			box.clearContents()
		else:
			box=QTableWidget(row,col)
		header=box.horizontalHeader()
		header.setSectionResizeMode(0,QHeaderView.Stretch)
		box.horizontalHeader().hide()
		box.verticalHeader().hide()
		box.setShowGrid(False)
		box.setSelectionBehavior(QTableWidget.SelectRows)
		box.setSelectionMode(QTableWidget.SingleSelection)
		box.setEditTriggers(QTableWidget.NoEditTriggers)
		sigmap_run=QSignalMapper(self)
		sigmap_remove=QSignalMapper(self)
		sigmap_install=QSignalMapper(self)
		applist={}
		for path in paths:
			sw_local=False
			if "home/" in path:
				sw_local=True
			if not os.path.isdir(path):
				continue
			for app in os.listdir(path):
				if app in applist.keys():
					if sw_local==False:
						applist[app]=path
				else:
					applist[app]=path
		for app,path in applist.items():
			if app.endswith(".appimage"):
				box.setRowCount(row+1)
				appBox=QHBoxLayout()
				appimage=("%s/%s"%(path,app))
				lbl=QLabel(app.replace(".appimage",""))
				lbl.setObjectName("managerLabel")
				if sw_local:
					print(path)
				btn_remove=QPushButton()
				btn_remove.setIcon(icn_trash)
				btn_remove.setIconSize(QSize(48,48))
#				btn_remove.setStyleSheet("""QPushButton{background: red;}""")
				btn_remove.setToolTip(_("Remove %s")%app)
				sigmap_remove.removeMappings(btn_remove)
				sigmap_remove.setMapping(btn_remove,appimage)
				btn_remove.clicked.connect(sigmap_remove.map)
				btn_run=QPushButton()
				btn_run.setIcon(icn_run)
				btn_run.setIconSize(QSize(48,48))
#				btn_run.setStyleSheet("""QPushButton{background: blue;}""")
				btn_run.setToolTip(_("Execute %s")%app)
				btn_run.setObjectName(str(row))
				sigmap_run.removeMappings(btn_run)
				sigmap_run.setMapping(btn_run,appimage)
				btn_run.clicked.connect(sigmap_run.map)
				box.setItem(row,0,QTableWidgetItem(app.replace(".appimage","")))
				box.setCellWidget(row,1,btn_run)
				box.setCellWidget(row,2,btn_remove)
				if "home/" in path:
					btn_install=QPushButton()
					btn_install.setIcon(icn_install)
					btn_install.setIconSize(QSize(48,48))
#					btn_install.setStyleSheet("""QPushButton{background: lightgreen;}""")
					btn_install.setToolTip(_("Install %s")%app)
					sigmap_install.removeMappings(btn_install)
					sigmap_install.setMapping(btn_install,appimage)
					btn_install.clicked.connect(sigmap_install.map)
					box.setCellWidget(row,3,btn_install)
				row+=1
		box.resizeRowsToContents()
		box.show()
		return (box,sigmap_run,sigmap_remove,sigmap_install)

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
			btn_desktop.setToolTip(_("Name: %s\nDescription: %s\nIcon: %s\nCategory: %s")%(desktop['name'],desktop['comment'],desktop['icon'],desktop['categories']))

		def _select_appimage():
			fdia=QFileDialog()
			fdia.setFileMode(QFileDialog.AnyFile)
			fdia.setNameFilter("appimages(*.appimage)")
			if (fdia.exec_()):
				appimage=fdia.selectedFiles()[0]
				appimage_name=os.path.basename(appimage).rstrip(".appimage")
				action="install"
				lbl_action.setText(_("%s the application %s")%(action.capitalize(),appimage_name))
				btn_action.disconnect()
				btn_action.clicked.connect(lambda: self._install(appimage,desktop))

		self._debug("Loading installer...")
		tabInstall=QWidget()
		self.setWindowTitle("Appimage Manager")
		box=QVBoxLayout()
		deskbox=QHBoxLayout()
		btn_desktop=QPushButton("")
		btn_desktop.setObjectName("menuButton")
		lbl_desktop=QLabel(_("Push button to set the icon,\n name and category for the app\n or use default ones"))
		btn_desktop.setToolTip(_("Name: %s\nDescription: %s\nIcon: %s\nCategory: %s")%(desktop['name'],desktop['comment'],desktop['icon'],desktop['categories']))
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
		if appimage:
			lbl_action=QLabel(_("%s the application %s")%(action.capitalize(),appimage_name))
			btn_action.clicked.connect(lambda: self._install(appimage,desktop))
		else:
			lbl_action=QLabel(_("Press button to select an appimage for install"))
			btn_action.clicked.connect(_select_appimage)
		actionbox.addWidget(lbl_action,1,Qt.Alignment(0))
		icn_action=QtGui.QIcon.fromTheme("system-run")
		img_action=QLabel()
		img_action.setPixmap(icn_action.pixmap(QSize(64,64)))
		actionbox.addWidget(img_action,0,Qt.Alignment(2))
		btn_action.setLayout(actionbox)
		btn_action.setToolTip(_("Install appimage"))
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
#		box=QFormLayout()
		box=QGridLayout()
		lbl_icon=QLabel(_("Icon: "))
		lbl_icon.setObjectName("dlgLabel")
		inp_icon=QLineEdit(desktop['icon'])
		btn_icon=QPushButton()
		icn_desktop=QtGui.QIcon.fromTheme(icon)
		btn_icon.setIcon(icn_desktop)
		btn_icon.setIconSize(QSize(64,64))
		btn_icon.clicked.connect(_file_chooser)
		box.addWidget(lbl_icon,0,1,1,1)
		box.addWidget(btn_icon,1,1,3,1)
		lbl_name=QLabel(_("Name: "))
		lbl_name.setObjectName("dlgLabel")
		inp_name=QLineEdit(desktop['name'])
		inp_name.setPlaceholderText(_("Desktop name"))
		box.addWidget(lbl_name,0,0,1,1)
		box.addWidget(inp_name,1,0,1,1)
		lbl_cat=QLabel(_("Category: "))
		lbl_cat.setObjectName("dlgLabel")
		cmb_cat=QComboBox()
		cmb_cat.setSizeAdjustPolicy(0)
		th_categories=th_getCategories()
		th_categories.start()
		th_categories.signal.connect(_set_categories)
		box.addWidget(lbl_cat,2,0,1,1)
		box.addWidget(cmb_cat,3,0,1,1)
		lbl_desc=QLabel(_("Description: "))
		lbl_desc.setObjectName("dlgLabel")
		inp_desc=QLineEdit(desktop['comment'])
		inp_desc.setPlaceholderText(_("Description"))
		box.addWidget(lbl_desc,4,0,1,2)
		box.addWidget(inp_desc,5,0,1,2)
		btnBox=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
		btnBox.rejected.connect(dia.reject)
		btnBox.accepted.connect(_begin_save_desktop)
		box.addWidget(btnBox,6,0,1,2)
		dia.setLayout(box)
		dia.show()
		result=dia.exec_()
		return (desktop,result==QDialog.Accepted)
	#def _render_desktop_dialog

	def _show_message(self,msg,status=None):
		self.statusBar.setText(msg)
		if status:
			self.statusBar.show(status)
		else:
			self.statusBar.show()

	@pyqtSlot()
	def _install(self,appimage,desktop):
		
		retval=True
		self._debug("Installing %s"%(appimage))
		dst_path='/usr/local/bin/'
		try:
			(name,icon,comment,categories,exe)=self._generate_desktop(appimage,desktop)
			subprocess.check_call(["pkexec","/usr/share/appimage-manager/bin/appimage-helper.py","install",appimage,dst_path,name,icon,comment,categories,exe])
			self._show_message(_("%s installed"%name),"success")
		except Exception as e:
			self._debug(e)
			retval=False
			self._show_message(_("Install Failed"))
		self.update_signal.emit(retval)
		return (retval)
	#def _install

	def _remove_appimage(self,appimage):
		retval=False
		try:
			subprocess.check_call(["pkexec","/usr/share/appimage-manager/bin/appimage-helper.py","remove",appimage])
			retval=True
		except Exception as e:
			self._debug("Removing: %s"%e)
		return retval
	#def _remove
	
	def _run_appimage(self,appimage):
		def _run_result(result):
			return result
			if result==False:
				self._show_message(_("Error executing %s"%appimage))

		th_run=th_runApp(appimage)
		th_run.start()
		th_run.signal.connect(_run_result)
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
		#managerLabel{
			font=20px Roboto;
			font-weight:bold;
		}
		#scrollbox{
			border:0px 0px 0px 0px;
			margin:0px;
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

	#dlgLabel{
		font:12px Roboto;
		margin:0px;
		border:0px;
		padding:3px;
	}
	
	QLineEdit{
		border:0px;
		border-bottom:1px solid grey;
		padding:1px;
		font:14px Roboto;
		margin-right:6px;
	}
	"""
	return(css)
	#def _define_css

#_debug("Init %s"%sys.argv)
err=0
action=""
appimage=""
args=sys.argv[1:]
while args:
	arg=args.pop()
	if os.path.isfile(arg):
		appimage=arg
	elif "-m"==arg or "--manage"==arg:
		action="manage"
	elif "-i"==arg or "--install"==arg:
		action="install"
if appimage and not action:
	action="run"
elif not appimage:
	action="manage"
if action=="install" or action=='manage':
	app=QApplication(["Appimage Manager"])
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
