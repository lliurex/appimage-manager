#!/usr/bin/env python3
import sys
import os
from PySide2.QtWidgets import QApplication
from QtExtraWidgets import QStackedWindow
import gettext
gettext.textdomain('appimage-manager')
_ = gettext.gettext
if len(sys.argv)<=1:
	app=QApplication(["Appimage Manager"])
	config=QStackedWindow()
	if os.path.islink(__file__)==True:
		abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
	else:
		abspath=os.path.dirname(__file__)
	config.addStacksFromFolder(os.path.join(abspath,"stacks"))
	config.setBanner("/usr/share/appimage-manager/rsrc/appimage_banner.png")
	config.setIcon("appimage-manager")
	config.show()
	config.setMinimumWidth(config.width()*1.3)
	config.setMinimumHeight(config.width()*0.7)
	app.exec_()
else:
	action=sys.argv[1]
	if action.lower().replace("-","")=="i" or action.lower()=="install":
		action="install"
	elif action.lower().replace("-","")=="r" or action.lower()=="remove":
		action="remove"
	else:
		print("Usage: {} [option] [parms]\n".format(sys.argv[0]))
		print("\t-i||--install url [name]: Download and install the given url. Name is optional")
		print("\t-r||--remove name: Remove the appimage and its associated desktop\n")
		sys.exit(1)
	if action=="install":
		os.execv("appimage-helper",("appimage-helper","install {}".format(" ".join(sys.argv[2:]))))
	elif action=="remove":
		os.execv("appimage-helper",("appimage-helper","remove {}".format(" ".join(sys.argv[2:]))))
