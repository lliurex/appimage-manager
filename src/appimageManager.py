#!/usr/bin/env python3
import sys
import os
from PySide2.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig
app=QApplication(["AppimageManager"])
config=appConfig("AppimageManager",{'app':app})
config.setRsrcPath("/usr/share/appimage-manager/rsrc")
config.setIcon('x-appimage')
config.setBanner('appimage_banner.png')
config.setWiki('http://wiki.edu.gva.es/lliurex/tiki-index.php?page=Aplicacions-AppImage-al-LliureX')
config.setBackgroundImage('drop_file.svg')
config.setConfig(confDirs={'system':'/usr/share/appimage-manager','user':'%s/.config'%os.environ['HOME']},confFile="appimage-manageer.conf")
config.Show()
config.setFixedSize(config.width(),config.height())

app.exec_()
