#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot
import gettext
gettext.textdomain('appimage-installer')
_ = gettext.gettext

err=0
dbg=True

RSRC="/usr/share/appimage-installer/rsrc"

def _debug(msg):
	if dbg:
		print("Appimage: %s"%msg)
		with open("/tmp/a","a") as f:
			f.write("%s\n"%msg)
#def _debug

def _show_error(msg):
	_debug("Launch error %s"%msg)
	dia=QDIalog()
	dia.setWindowTitle("Appimage Error")
	lbl_err=QLabel("%s"%msg)
	dia.exec_()
#def _show_error

def _generate_desktop(desktop):
	retval=True
	f_desktop="[Desktop Entry]\nVersion=1.0\nEncoding=UTF-8\nType=Application\n"
	for key,value in desktop.items():
		f_desktop+="%s=%s\n"%(key,value)
	try:
		_debug("/usr/share/applications/%s.desktop"%desktop['Name'])
		with open ("/usr/share/applications/%s.desktop"%desktop['Name'],'w') as f:
			f.writelines(f_desktop)
	except Exception as e:
		retval=False
		_debug(e)
	return retval
#def _generate_desktop
	

def _render_gui(action,appimage):
	appimage_name=os.path.basename(appimage).rstrip(".appimage")
	desktop={'Icon':'x-appimage','Name':appimage_name,'Comment':'','Categories':'Other'}
	app=QApplication([])
	app.instance().setStyleSheet(_define_css())
	mw=QWidget()
	mw.setWindowTitle("Appimage Manager")
	box=QVBoxLayout()
	img_banner=QLabel()
	img=QtGui.QPixmap("%s/appimage_banner.png"%RSRC)
	img_banner.setPixmap(img)
	icn_desktop=QtGui.QIcon.fromTheme("x-appimage")
	btn_desktop=QPushButton(_("Push button to set the icon,\n name and category for the app\n or use default ones"))
	btn_desktop.setIcon(icn_desktop)
	btn_desktop.setIconSize(QSize(64,64))
	btn_desktop.setLayoutDirection(1)
	btn_desktop.clicked.connect(lambda: _set_desktop_info(desktop))
	icn_action=QtGui.QIcon.fromTheme("system-run")
	btn_action=QPushButton(_("%s the application %s")%(action.capitalize(),appimage_name))
	btn_action.setIcon(icn_action)
	btn_action.setIconSize(QSize(64,64))
	btn_action.setLayoutDirection(1)
	btn_action.clicked.connect(lambda: _install(appimage,desktop))
	box.addWidget(img_banner)
	box.addWidget(btn_desktop)
	box.addWidget(btn_action)
	mw.setLayout(box)
	mw.show()
	app.exec_()

@pyqtSlot()
def _set_desktop_info(desktop):
	
	return desktop
#def _set_desktop_info

@pyqtSlot()
def _install(appimage,desktop):
	
	retval=True
	_debug("Installing %s"%(appimage))
	dst_path='/usr/local/bin/%s'%os.path.basename(sys.argv[1])
	try:
			#		shutil.copy2(appimage,dst_path)
		subprocess.check_call(["/usr/share/appimage-manager/bin/appimage-helper.py","install",appimage,dst_path,desktop])
	except Exception as e:
		_debug(e)
		retval=False
	if retval:
		_debug("Generating desktop...")
		retval=_generate_desktop(desktop)
	return (retval)
#def _install

def _remove(appimage):
	pass
#def _remove

def _define_css():
	css="""
	QPushButton{
		padding: 6px;
		margin:6px;
		font: 14px Roboto;
		color:black;
	}
	"""
	return(css)
#def _define_css
	
err=0
if len(sys.argv)==2:
	action="run"
	appimage=sys.argv[1]
elif len(sys.argv)==3:
	action="install"
	appimage=sys.argv[2]
else:
	_debug("Bad argument %s"%sys.argv)
	exit(1)
if action=="install":
	_render_gui(action,appimage)
else:
	_debug("Executing %s"%appimage)
	try:
		subprocess.check_call(["/usr/share/appimage-manager/bin/appimage-helper.py","run",appimage])
	except Exception as e:
		_debug(e)
		_show_error(e)
exit(0)