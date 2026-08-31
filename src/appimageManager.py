#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import QApplication
from QtExtraWidgets import QStackedWindow
import gettext
gettext.textdomain('appimagemanager')
_ = gettext.gettext
app=QApplication(["Appimage Manager"])
config=QStackedWindow()
if os.path.islink(__file__)==True:
	abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
else:
	abspath=os.path.dirname(__file__)
config.addStacksFromFolder(os.path.join(abspath,"stacks"))
config.setBanner("/usr/share/appimage-manager/rsrc/appimage_banner.png")
#config.setWiki("https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Repoman-en-Lliurex-21")
config.setIcon("appimage-manager")
config.show()
config.setMinimumWidth(config.width()*1.1)
config.setMinimumHeight(config.width()*0.8)
app.exec()
