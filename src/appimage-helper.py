#!/usr/bin/env python3
import sys
import shutil
import os
import subprocess
from app2menu import App2Menu

err=0
dbg=True

def _debug(msg):
	if dbg:
		print("Helper: %s"%msg)
#def _debug

if sys.argv[1]=='install':
	_debug("Installing %s %s"%(sys.argv[2],sys.argv[3]))
	appimage=sys.argv[2]
	path=sys.argv[3]
	desktop_name=sys.argv[4]
	desktop_icon=sys.argv[5]
	desktop_comment=sys.argv[6]
	desktop_categories=["%s"%sys.argv[7]]
	desktop_exe=sys.argv[8]
	_debug("Name: %s\nIcon: %s"%(desktop_name,desktop_icon))
	#install app
	os.chmod(appimage,0o755)
	shutil.copy2(appimage,path)
	#Generate desktop
	menu=App2Menu.app2menu()
	menu.set_desktop_info(desktop_name,desktop_icon,desktop_comment,desktop_categories,desktop_exe)
#	try:
#		with open ("/usr/share/applications/%s.desktop"%os.path.basename(appimage),'w') as f:
#			f.writelines(desktop)
#	except Exception as e:
#		retval=False
#		_debug(e)

#def _generate_desktop
	try:
		subprocess.check_call(['gtk-update-icon-cache','/usr/share/icons/hicolor/'])
	except:
		err=2
	_debug("Installed %s %s"%(sys.argv[2],sys.argv[3]))
elif sys.argv[1]=='run':
	appimage=sys.argv[2]
	os.chmod(appimage,0o744)
	subprocess.check_call([appimage])
elif sys.argv[1]=='remove':
	pass
exit(err)

