#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------
# Xen coalesce-leaf tool.
# v1.0

import sys
import time
import os
import re
import shutil
import getpass
import commands

myversion="1.0"
hcmd = commands.getoutput('xe pool-list params=master')
vms = commands.getoutput('xe vm-list is-control-domain=false power-state=running params=uuid')
vmsl = vms.lstrip()
vmsl_ = vmsl.split()
expr = "master"
s_count = 0

def cleanleaf():
	os.system('clear')
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print "! 				Running coalesce-leaf tool "+myversion+"                                                   !"
	print "! WARNING: If you don't know what this tool is supposed to do, this is a GOOD TIME TO QUIT without further adue. !"
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print
	Ox = str(raw_input('Proceed (Y/N): '))
	if str.upper(Ox) == "Y":
		print "Checking snapshots :"
		print
		print "!!! ATTENTION: Snapshots found: "+ '%.0d' %(s_count-5)+"."
		print "!!! If your intention is to reclame the space of existing snapshots, first you have to delete it, this script WILL NOT do it for you."
		print "!!! I can however proceed and reclaim storage space of already deleted snapshots."
		print
		Px = str(raw_input('Proceed ? (Y/N): '))
		if str.upper(Px) == "Y":
			print
			match = re.search(expr,hcmd)
			if match is not None:
				matched = re.search(':.*',hcmd).group()
				print "Matched: "+matched
				HOSTUUID = re.search('[^:]\S*',matched).group()
				print "Appling plugin coalesce-leaf on host "+HOSTUUID.lstrip()
			else:
				print "Something is wrong, I couldn't find this OWN HOST UUID. Are you in the POOL MASTER?"
		else: 
			print "Exiting now. Goodbye"
		#commands here
		a = 0
		for i,vuuid in enumerate(vmsl_):
			while a < len(vmsl_) and len(vmsl_[a]) > 35:
				VMUUID = vmsl_[a]
				print '[cleanleaf] - Will execute : xe host-call-plugin host-uuid='+HOSTUUID.lstrip()+' plugin=coalesce-leaf fn=leaf-coalesce args:vm_uuid='+VMUUID
				os.popen('xe host-call-plugin host-uuid='+HOSTUUID.lstrip()+' plugin=coalesce-leaf fn=leaf-coalesce args:vm_uuid='+VMUUID)
				a = i+1
			else:
				a = i+1
	else:
		print "Exiting now. Goodbye"

cleanleaf()
