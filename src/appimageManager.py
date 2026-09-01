#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import QApplication
from QtExtraWidgets import QStackedWindow
import gettext
gettext.textdomain('appimage-manager')
_ = gettext.gettext
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
app.exec()
