#!/usr/bin/env python3
import sys
import shutil
import os
import subprocess

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
	desktop=sys.argv[4]
	#install app
	shutil.copy2(appimage,path)
	#Generate desktop
	try:
		with open ("/usr/share/applications/%s.desktop"%os.path.basename(appimage),'w') as f:
			f.writelines(desktop)
	except Exception as e:
		err=1
		_debug(e)

#def _generate_desktop
	try:
		subprocess.check_call(['gtk-update-icon-cache','/usr/share/icons/hicolor/'])
	except:
		err=2
elif sys.argv[1]=='run':
	appimage=sys.argv[2]
	os.chmod(appimage,0o744)
	subprocess.check_call([appimage])
elif sys.argv[1]=='remove':
	pass
exit(err)

