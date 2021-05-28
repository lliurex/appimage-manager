#!/usr/bin/python3

import sys
import os
import shutil
import magic
import tempfile
import json
import subprocess
import grp,pwd

dbg=False
retCode=0

def _debug(msg):
	if dbg:
		print("App installer: %s"%msg)
#def _debug

def _generate_install_dir():
	global retCode
	installDir=''
	try:
		installDir=tempfile.mkdtemp()
	except:
		_debug("Couldn't create temp dir")
		retCode=1
	os.chown(installDir,os.geteuid(),os.getgid())
	_debug("Install dir: %s"%installDir)
	return (installDir)
#def _generate_install_dir

def _get_app_info(app):
	global retCode
	appInfo={}
#	appInfo=installer.appManager().get_app_info(app)
	return (appInfo)
#def _get_deb_info

def _begin_install_package(app):
	global retCode
	mime=magic.Magic(mime=True)
	if ((os.path.isfile(app))):# and (mime.from_file(app)=='application/x-app-installer')):
		_generate_epi_file(app)
	else:
		_debug("%s is an invalid file %s"%(app,mime.from_file(app)))
		retCode=1
#def _begin_install_package

def _generate_epi_json(app):
	global retCode
	tmpDir=os.path.dirname(app)
	appName=os.path.basename(app)
	epiJson=''
	#retCode controls the return code of the previous operations 
	if not retCode:
		_debug("Generating json at %s"%tmpDir)
		epiJson="%s/%s.epi"%(tmpDir,appName.replace(" ","_"))
		epiFile={}
		epiFile["type"]="file"
		epiFile["pkg_list"]=[{"name":appName,'url_download':tmpDir,'version':{'all':appName}}]
		epiFile["script"]={"name":"%s/install_script.sh"%tmpDir,'remove':True,'download':True}
		epiFile["required_root"]=False
		epiFile["required_dconf"]=True
		try:
			with open(epiJson,'w') as f:
				json.dump(epiFile,f,indent=4)
			_debug("OK")
		except Exception as e:
			_debug("Error %s"%e)
			retCode=1
	return(epiJson)
#def _generate_epi_json

def _generate_epi_script(app):
	global retCode
	tmpDir=os.path.dirname(app)
	appName=os.path.basename(app)
	try:
		#Copy the icon to temp folder
		with open("%s/install_script.sh"%tmpDir,'w') as f:
			f.write("#!/bin/bash\n")
			f.write("DESTDOWNLOAD=\"/var/cache/epi-downloads\"\n")
			f.write("ACTION=\"$1\"\n")
			f.write("case $ACTION in\n")
			f.write("\tremove)\n")
			f.write("\t\trm -fr %s\n"%app)
			f.write("\t\t;;\n")
			f.write("\ttestInstall)\n")
			f.write("\t\techo ""\n")
			f.write("\t\t;;\n")
			f.write("\tdownload)\n")
			f.write("\t\ttouch /tmp/abc\n")
			f.write("\t\t;;\n")
			f.write("\tinstallPackage)\n")
			f.write("\t\techo %s\n"%app)
			f.write("\t\tcp %s $HOME/Applications\n"%(app))
			f.write("\t\tchmod +x $HOME/Applications/%s\n"%(appName))
			f.write("\t\techo %s is now available at appimage-manager"%appName)
			f.write("\t\t;;\n")
			f.write("\tgetInfo)\n")
			f.write("\t\techo \"\"\n")
			f.write("\t\t;;\n")
			f.write("esac\n")
			f.write("exit 0\n")
	except Exception as e:
		_debug("%s"%e)
		retCode=1
	os.chmod("%s/install_script.sh"%tmpDir,0o755)
#def _generate_epi_script

def _generate_epi_file(app):
	global retCode
	installDir=_generate_install_dir()
	if installDir:
		#copy app to installDir
		try:
			appName=os.path.basename(app)
			shutil.copyfile(app,"%s/%s"%(installDir,appName))
			app="%s/%s"%(installDir,appName)
			_debug("%s copied to %s"%(app,installDir))
		except Exception as e:
			_debug("%s couldn't be copied to %s: %s"%(app,installDir,e))
			retCode=1
		
		if not retCode:
			epiJson=_generate_epi_json(app)
			_generate_epi_script(app)
			if not retCode:
				_debug("Launching %s"%epiJson)
				subprocess.run(['epi-gtk',epiJson])
			else:
				subprocess.run(['epi-gtk',"--error"])
		else:
			subprocess.run(['epi-gtk',"--error"])
	elif retCode:
		subprocess.run(['epi-gtk',"--error"])
installFile=sys.argv[1]
_begin_install_package(installFile)

