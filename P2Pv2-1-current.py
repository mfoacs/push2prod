#!/usr/bin/python
# -*- coding: utf-8 -*-
# P2Pv2.py (version 2.0 - 14/10/2010)
#
# Changelog:
# 31.01.2012 	MDA	V2 Creation from push2prod v1.1.
#			New Features include sending email with results and advanced logging
#############################################################################################

# Imports

import sys
import time
import os
import getpass
import re
import curses
import shutil
import tarfile
import smtplib
from email.mime.text import MIMEText
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, FileTransferSpeed, FormatLabel, Percentage, ProgressBar, ReverseBar, RotatingMarker, SimpleProgress, Timer
from socket import gethostname, gethostbyname

# Global VARS

ConfFolder="/home/wiseweb/public_html/conf/"
RootFolder="P2P_ROOT"
PROD="wiseweb@vos02.wisekey.ch:"
BackupFolder=".snapshots"
logfolder="/home/wiseweb/logs/"
archived="archive"
oP=""
Sx=""
whoami = getpass.getuser()
connectionIP = gethostbyname(gethostname())

MailServer="mailcleaner.wisekey.ch"
mailto=['techalert@wisekey.com']
mailtoTask=['techalert@wisekey.com']
mailto=['supportwa@wisekey.com']
mailtech=['techalert@wisekey.com']
mailtoAdmin=['supportwa@wisekey.com']

			
def sendMail(to, subject, server):

	sender="P2Pv2 <prod@wisekey.com>"
	headers="From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, to, subject)
	fp = open(filetoday, 'rb')
	# Create a text/plain message
	msg = MIMEText(fp.read())
	fp.close()
	message=headers + msg.as_string()
	mailServer=smtplib.SMTP(server)
	mailServer.sendmail(sender, to, message)
	mailServer.quit()


# Write the log file
def Write2Log(LogText):
	import datetime	
	now=GetTime()
	year=now[0]
	month=now[1]
	day=now[2]
	hour=now[3]
	minutes=now[4]
	sec=now[5]
	global filetoday
	filetoday=LocationFolder+"/.xlogs/P2P-"+`year`+`month`+`day`+"-"+`hour`+`minutes`+".log"
	fileHandle=open (filetoday, 'a')
	TextFile='\n'+time.asctime(now)
	TextFile=TextFile+LogText
	fileHandle.write(TextFile)
	fileHandle.close()

# VSite checks/updates the deployed site version
def VSite(siteRootF):
	versionSiteF=siteRootF+"/"+".version"
	svninf=siteRootF+"/.svn"+"entries"
	fileHandle=open (versionSiteF, 'a')
	svnfileinfo=open (svninf, 'r')
	fileHandle.write(svnfileinfo)
	fileHandle.close()
	

# Clear the console screen
def clearscreen():
	os.system('clear')
	#stdscr = curses.initscr()
	#curses.echo()
	#stdscr.keypad(1)
	#begin_x = 20 ; begin_y = 7
	#height = 5 ; width = 40
	#win = curses.newwin(height, width, begin_y, begin_x)

def GetTime():
	now = time.localtime(time.time())
	return now

def RestoreTAR(source,dest):
	if "untarred" in source:
		print "This archive has already been restored, skipping."
		NsXe[10](LogText=" [WARN-1] : Aborted attempt to restore an already restored archive: "+source+" ---- "+"\n")
		NsXe[6](dest)
	else:
                basefolder = '/home/wiseweb/public_html'
		archiveTar = dest+"/"+BackupFolder+"/"+archived+"/"+source
		tar = tarfile.open(archiveTar)
		m = tar.extractall(basefolder)
		tar.close()
		restored = ".untarred"
		shutil.move(archiveTar, archiveTar+restored)
		NsXe[10](LogText=" [INFO-3] : Successfully restored backup from "+archiveTar+" to "+dest+" ---- "+"\n")
		NsXe[7]()
		NsXe[6](dest)
	
# Synchronize files from A to B

'''
def syncfiles(execComm):
	os.system(execComm)
   	NsXe[10](LogText=" [INFO] : Finished PUSH2PROD from "+localFolder+" to "+syncSite+" : %d Files were successfully transferred" %(file_count,)+"\n")
   	sendMail("techalert@wisekey.com","Finished PUSH2PROD from "+localFolder+" to "+syncSite,MailServer)
	print ">>>> Cave Johnson here, your Boss, Job DONE ! Good Job Computer <<<<"


'''

def syncfiles(execComm):
	class CrazyFileTransferSpeed(FileTransferSpeed):
		"It's bigger between 45 and 80 percent"
		def update(self, pbar):
			if 45 < pbar.percentage() < 80:
				return FileTransferSpeed.update(self,pbar)
			else:
				return FileTransferSpeed.update(self,pbar)
	widgets = [CrazyFileTransferSpeed(),' <<<', Bar(), '>>> ', Percentage(),' ', ETA()]
	pbar = ProgressBar(widgets=widgets, maxval=10000000)
	# DO SYNC HERE
	os.popen(execComm)
	pbar.start()
	for i in range(2000000):
		pbar.update(5*i+1)
   	pbar.finish()
   	NsXe[10](LogText=" [INFO-2] : Finished PUSH2PROD from "+localFolder+" to "+syncSite+" : %d Files were successfully transferred" %(file_count,)+"\n")
   	sendMail("techalert@wisekey.com","Finished PUSH2PROD from "+localFolder+" to "+syncSite,MailServer)
	print ">>>> Cave Johnson here, your Boss, Job DONE ! Good Job Computer <<<<"


# TODO
'''
CLEAN UP FUNCTIONS (PERMISSIONS + EVENTUAL SVN ENTRIES)
rm -Rfv $(find . -name .svn)
'''

# Prepare Options to synchronize from Remote to Local
def bckRemote():
	"Prepare Options to synchronize from Remote to Local"		
	print "-------------------------------------------------------------------"
	print "PATH: "+localFolder
	print "Remote Source: "+syncSite
	print "Backup Folder: "+localFolder+"/"+BackupFolder
	snapDir = localFolder+"/"+BackupFolder
	print "-------------------------------------------------------------------"
	print "Command to execute: "+syncSite+" "+snapDir
	print "You can find my logs here: "+filetoday
	print "-------------------------------------------------------------------"
	# Check if the folder exists first, create it if necessary
	if not os.path.exists(snapDir):
		print "Directory doesn't exist, creating a new one"		
		os.makedirs(snapDir)
		cmd = ('rsync -pravzhWm --progress --log-file='+filetoday+' '+EXCLUSION_OPTS+' '+syncSite+' '+snapDir)
	else:
		cmd = ('rsync -pravzhWm --progress --log-file='+filetoday+' '+EXCLUSION_OPTS+' '+syncSite+' '+snapDir)
	# print cmd
	archiveFolder = snapDir+"/"+archived
	# We need an archive folder too
	if not os.path.exists(archiveFolder):
		os.makedirs(archiveFolder)
	else:
		print "Archive folder found, compressing previous backup and move it to archive"
		now=GetTime()
		month=now[1]
		year=now[0]
		hour=now[3]
		day=now[2]
		minutes=now[4]
		sec=now[5]
		archive_name = snapDir+"/"+`year`+`month`+`day`+"-"+`hour`+"h"+`minutes`+"m"+`sec`+"s"
		# print archive_name
		TarFile = shutil.make_archive(archive_name, 'gztar', snapDir)
		shutil.move(TarFile, archiveFolder)
	# call the synch function
	NsXe[2](cmd)


# Restore a backup and then synchronize from Local to Remote
def restoreB4sync():
	"Restore a backup from an archived site"
	print "Get the list of backups and chose one to restore"
	snapDir = localFolder+"/"+BackupFolder
	print snapDir
	archives = snapDir+"/"+archived
	print archives
	tarFiles = os.listdir(archives)
	for i,conf in enumerate(tarFiles):
		print i+1, conf
	Rx = input('Restore from which version ?: ')
	Sx = str(raw_input('Are you sure? If you answer YES, the local contents of the SITE will be OVERWRITTEN with the selected backup and synchronized with the PROD (Y/N): '))
	if str.upper(Sx) == "Y":
		tarFile = tarFiles[Rx-1]
		print tarFile, localFolder
		NsXe[9](tarFile,localFolder)
		sendMail("techalert@wisekey.com","Finished PUSH2PROD: restored backup from "+tarFile,MailServer)
#		NsXe[5]()
	else:
		print "Operation Aborted by user. Exiting now."		
		NsXe[4]()
		NsXe[5]()


# Pretty obvious isn't it ?
def cleanExit():
	print "  ---- Cave Johnson here, your Boss: go back to work "+whoami+" ! ----  "
	#curses.nocbreak(); 
	#stdscr.keypad(0); 
	#curses.noecho();
	#curses.endwin();

# Check what there is to be synchronized
def sOptions(lFolder):
	"What do to do with the select folder/site "
	global localFolder
	global file_count
	file_count = 0
	localFolder = lFolder
	global syncSite
	syncSite = PROD+lFolder
	global EXCLUSION_OPTS
	EXCLUSION_OPTS="--exclude-from "+localFolder+"/.nP2P"
	cmd = ('rsync -ravzOn --include .htaccess --progress '+EXCLUSION_OPTS+' '+lFolder+'/* '+syncSite)
	for i,fileList in enumerate(os.popen(cmd)):
		file_count = i+1	
		print "Counting files: "+'{0}\r'.format(file_count),
	print

	NsXe[10](LogText=" [INFO] : Found %d files to synchronize " % (file_count,)+"\n")
	if file_count > 0:
		print "		Found %d files to synchronize :" % (file_count,) +"\n"
		print "			1 - Backup Remote Site and Quit"
		print "			2 - Synchronize from Local to Remote >> "+lFolder+"/* "+syncSite
		print "			3 - Restore from a Local backup and synchronize to Remote"
		print "			4 - Exit the application now"
		oP = input('Action: ')
		if oP == 2:
			cmd = ('rsync -prazhWO --include .htaccess --progress --log-file='+filetoday+' '+EXCLUSION_OPTS+' '+lFolder+'/* '+syncSite)
			NsXe[1]
			NsXe[2](cmd)
		else:
			NsXe[oP]()
	else:
	  print "Found %d files to synchronize :" % (file_count,) +"\n"
	  print "Sychronize another site ?"
	  qP = input('Yes(Y)/No(N): ')
	  if str.upper(qP) == "Y":
	    ProdDestFolder()
	  else:
	    NsXe[4]()


# Get the configuration file and file locations to synchronize
def ProdDestFolder():
	global LocationFolder
	"Get the RootFolder value from the Apache Configuration File"	
	listFolders = os.listdir(ConfFolder)
	for i,conf in enumerate(listFolders):
		print i+1, conf
	x = input('Type Site Number #: ')
	if listFolders[x-1] < len(listFolders):
		print "Out of range"
		print len(listFolders)
	else:
		with open(ConfFolder+listFolders[x-1]) as f:
	    		for line in f:
				if re.search(RootFolder,line):
					LocationFolder = re.search('/.*',line).group()
					NsXe[10](LogText=" [START] : User "+whoami+" connected from IP: "+connectionIP+"\n")
					NsXe[10](LogText=" [INFO-1] : Starting PUSH2PROD on "+LocationFolder+"\n")
					NsXe[6](LocationFolder)

# Dictionary
NsXe = {1 : bckRemote,
	2 : syncfiles,
	3 : restoreB4sync,
	4 : cleanExit,
	5 : ProdDestFolder,
	6 : sOptions,
	7 : clearscreen,
	8 : GetTime,
	9 : RestoreTAR,
	10 : Write2Log,
	11 : VSite,
} 


#Call function to start
# stdscr = curses.initscr()
# curses.noecho()

NsXe[7]()
print "-------------------------------------------------------------------"
print "ConfFolder    =    "+ConfFolder
print "PROD          =    "+PROD
print "Logs          =    "+logfolder
print "Notifications =    ", str(mailto)
print "-------------------------------------------------------------------"
ProdDestFolder()
exit(0)