#!/usr/bin/env python3
import sys
import shutil
import os
import subprocess

err=0
dbg=False

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
	try:
		subprocess.check_call(['gtk-update-icon-cache','/usr/share/icons/hicolor/'])
	except:
		err=1
elif sys.argv[1]=='run':
	appimage=sys.argv[2]
	os.chmod(appimage,0o744)
	subprocess.check_call([appimage])
elif sys.argv[1]=='remove':
	pass
exit(err)

