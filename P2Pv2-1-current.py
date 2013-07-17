#!/usr/bin/python
# -*- coding: utf-8 -*-
# P2Pv2-67426eaf86
# CHANGELOG:
# 31.01.2012 	MDA	   V2 Creation from push2prod v1.1.: New Features include sending email with results and advanced logging
# 30.10.2012    MDA    v3.0.0 Classes, progress bar, archive handling improved.
# 17.07.2013    MDA    v3.0.1 Added handling file permissions correctly. (git show-ref refs/heads/master | cut -d " " -f 1 | cut -c 31-40)
# TODO                 Avanced Menu with site version and remote files delete option.
###############################################################################################################################



import curses
import os
import commands
import getpass
from socket import gethostname, gethostbyname
import re
import time
import shutil
import smtplib
from email.mime.text import MIMEText
from types import NoneType
import tarfile

# Global VARS
ConfFolder="/home/wiseweb/public_html/conf/"
RootFolder="P2P_ROOT"
PROD="wiseweb@vos02.wisekey.ch"
whoami = getpass.getuser()
connectionIP = gethostbyname(gethostname())
baselogstring = whoami+'@'+connectionIP
# operating_agents = ('NDB','KLB','MDA','MRO','PFU','OTHER')
listFolders = commands.getoutput('ls '+ConfFolder)
listStack = listFolders.split()
x = -1

permissions = '0775'
pre_owner = 'wwwrun:www'
post_owner = 'wiseweb:www'


MailServer="mailcleaner.wisekey.ch"
mailtoProd=['techalert@wisekey.com']
mailtoAdmin=['supportwa@wisekey.com']


def send_mail(attach,to,subject,server):
    "Send the notification message"
    sender="P2Pv2 <prod@wisekey.com>"
    headers="From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, to, subject)
    fp = open(attach, 'rb')
    # Create a text/plain message
    msg = MIMEText(fp.read())
    fp.close()
    message=headers + msg.as_string()
    mailServer=smtplib.SMTP(server)
    mailServer.sendmail(sender, to, message)
    mailServer.quit()

def write2log(logtext):
    "Writing messages to the logfile"
    fileHandle=open (logfile, 'a')
    fileHandle.write(logtext+'\n')
    fileHandle.close()

class ProgressBar:
    """ Creates a text-based progress bar. Call the object with the `print'
        command to see the progress bar, which looks something like this:

        [=======>        22%                  ]

        You may specify the progress bar's width, min and max values on init.
    """

    def __init__(self, minValue = 0, maxValue = 100, totalWidth=80):
        self.progBar = "[]"   # This holds the progress bar string
        self.min = minValue
        self.max = maxValue
        self.span = maxValue - minValue
        self.width = totalWidth
        self.amount = 0       # When amount == max, we are 100% done
        self.updateamount(0)  # Build progress bar string

    def updateamount(self, newAmount = 0):
        """ Update the progress bar with the new amount (with min and max
            values set at initialization; if it is over or under, it takes the
            min or max value as a default. """
        if newAmount < self.min: newAmount = self.min
        if newAmount > self.max: newAmount = self.max
        self.amount = newAmount

        # Figure out the new percent done, round to an integer
        diffFromMin = float(self.amount - self.min)
        percentDone = (diffFromMin / float(self.span)) * 100.0
        percentDone = int(round(percentDone))

        # Figure out how many hash bars the percentage should be
        allFull = self.width - 2
        numHashes = (percentDone / 100.0) * allFull
        numHashes = int(round(numHashes))

        # Build a progress bar with an arrow of equal signs; special cases for
        # empty and full
        if numHashes == 0:
            self.progBar = "[>%s]" % (' '*(allFull-1))
        elif numHashes == allFull:
            self.progBar = "[%s]" % ('='*allFull)
        else:
            self.progBar = "[%s>%s]" % ('='*(numHashes-1),
                                        ' '*(allFull-numHashes))

        # figure out where to put the percentage, roughly centered
        percentPlace = (len(self.progBar) / 2) - len(str(percentDone))
        percentString = str(percentDone) + "%"

        # slice the percentage into the bar
        self.progBar = ''.join([self.progBar[0:percentPlace], percentString,
                                self.progBar[percentPlace+len(percentString):]
                                ])

    def __str__(self):
        return str(self.progBar)
    
    def __call__(self, value):
        """ Updates the amount, and writes to stdout. Prints a carriage return
            first, so it will overwrite the current line in stdout."""
        print '\r',
        self.updateAmount(value)
        sys.stdout.write(str(self))
        sys.stdout.flush()


class SiteClass:
    'A site is website, what else would it be?'
    def __init__(self,apacheconf,prodserver):
        self.apacheconf = apacheconf
        self.prodserver = prodserver
        self.errors = []
        
    def show_progress(self):
        'A progress bar'
        #Create a window object.
        win = curses.newwin(3,32,18,10)
        # Add the Border
        win.border(0)
        # Current text: Progress
        win.addstr(1,1,"Progress ")
        # This is to move the progress bar per iteration.
        pos = 10
        # Random number I chose for demonstration.
        for i in range(15):
            # Add '.' for each iteration.
            win.addstr(1,pos,"%")
            # Refresh or we'll never see it.
            win.refresh()
            # Here is where you can customize for data/percentage.
            time.sleep(0.07)
            # Need to move up or we'll just redraw the same cell!
            pos += 1
        # Current text: Progress ............... Done!
        win.addstr(1,26,"Done!")
        # Gotta show our changes.
        win.refresh()
        time.sleep(0.5)
    
    def p2p_root(self,pattern):
        'Get the root folder in the Apache conf file'
        self.pattern = pattern
        with open(self.apacheconf) as f:
            for line in f:
                if re.search(self.pattern,line):
                    self.rootfolder = re.search('/.*',line).group()
                    return self.rootfolder
    
    
    def permsowner(self,dest_folder,change_type,owner_or_mode):
        'Changes ownership of the remote folder'
        self.chtype = change_type
        self.ownerormode = owner_or_mode
        self.dest_folder = dest_folder
        # either chown or chmod. 
        if self.chtype == 'chown':
            self.permscomm = 'ssh -l wiseweb vos02 sudo /bin/chown '+self.ownerormode+' '+self.dest_folder+'/* -Rfv'
        else:
            #os.setuid(0)
            self.permscomm = 'ssh -l wiseweb vos02 sudo /bin/chmod '+self.ownerormode+' '+self.dest_folder+'/* -Rfv'
        return os.popen(self.permscomm)
    
    
    def p2p_now(self,command):
        'execute a synchronizaton command with the given parameters'
        self.command = command
        self.progress = self.show_progress()
        return os.popen(self.command),self.progress
    
    def filetoday(self):
        'Log file'
        self.now = time.localtime(time.time())
        self.year = self.now[0]
        self.month = self.now[1]
        self.day = self.now[2]
        self.hour = self.now[3]
        self.minutes = self.now[4]
        self.seconds = self.now[5]
        self.logfolder = self.rootfolder+'/.xlogs'
        self.timestamp = `self.year`+`self.month`+`self.day`+"-"+`self.hour`+'h'+`self.minutes`+'m'+`self.seconds`+'s'
        self.filenow = `self.year`+`self.month`+`self.day`+"-"+`self.hour`+'h'
        if not os.path.exists(self.logfolder):
            os.makedirs(self.logfolder)
        return self.filenow
        
    def countfiles(self):
        'Counting files to be synchronized'
        self.count = 0
        self.syncsite = self.prodserver+':'+self.rootfolder
        self.exclusions = "--exclude-from "+self.rootfolder+"/.nP2P"
        self.cmdcount = ('rsync -rvzOn --include .htaccess --progress '+self.exclusions+' '+self.rootfolder+'/* '+self.syncsite)
        for i,fileList in enumerate(os.popen(self.cmdcount)):
            self.count = i+1
            #print "File count: "+'{0}\r'.format(self.count),
        return self.count-4
    
    def siteversion(self):
        'Gets svn site checkout version if present'
        self.version = (os.popen('svn up | grep Revision'))
        return self.version
        
    def cleanup(self,flst):
        'Cache folders deletion'
        self.flst = flst
        for i,folderF in enumerate(self.flst):
            cleancmd = 'ssh '+self.prodserver+' rm -v '+self.rootfolder+'/'+folderF+'/*'
            self.p2p_now(cleancmd)

    def backup2archive(self):
        'Makes a backup of the remote site'
        self.snapshots = self.rootfolder+"/.snapshots/"
        self.archivefolder = self.rootfolder+"/.archive/"
        self.archivefile = self.archivefolder+self.filetoday()
        if not os.path.exists(self.snapshots):
            os.makedirs(self.snapshots)
            self.cmdbck = ('rsync -rvzhWm --progress --log-file='+self.logfolder+"/P2P-"+self.filetoday()+'.log '+self.exclusions+' '+self.syncsite+' '+self.snapshots)
        else:
            self.cmdbck = ('rsync -rvzhWm --progress --log-file='+self.logfolder+"/P2P-"+self.filetoday()+'.log '+self.exclusions+' '+self.syncsite+' '+self.snapshots)
        if not os.path.exists(self.archivefolder):
            #print "No archive folder found. Creating one..."
            os.makedirs(self.archivefolder)
        self.madeit = self.p2p_now(self.cmdbck)
        self.archived = shutil.make_archive(self.archivefile,'gztar',self.snapshots)
        return self.madeit, self.archived
    
    def archivecount(self):
        'Get the list of backups a site has'
        self.archivefolder = self.rootfolder+"/.archive/"
        self.tarFiles = commands.getoutput('ls '+self.archivefolder)
        return self.tarFiles
    
    def restorearchive(self,archivename,restorepoint):
        'Restore the archive to a TMP directory and deletes the archive file'
        self.archivename = self.archivefolder+archivename
        self.restorepoint = self.rootfolder+"/"+restorepoint
        self.message = ""
        if not os.path.exists(self.restorepoint):
            self.message = "Creating the restore point and decompressing archive into..."
            os.makedirs(self.restorepoint)
        else:
            self.message = "Previous archive folder found. Cleaning up before restore..."
            shutil.rmtree(self.restorepoint)
            time.sleep(0.05)
        tar = tarfile.open(self.archivename)
        m = tar.extractall(self.restorepoint)
        tar.close()
        os.remove(self.archivename)
        return tar, m, self.archivename, self.restorepoint,  self.show_progress(), self.message



def s_options(rootFolder):
    'What do to do with the select folder/site'
    global file_count
    file_count = syncsite.countfiles()
    localFolder = rootFolder
    global logging
    global logfile
    logging = syncsite.filetoday()
    logfile = syncsite.logfolder+"/P2P-"+logging+'.log'
    # Change owner to wiseweb, initialize instance of persmowner
    PermsOrOwner = syncsite.permsowner(localFolder,'chown',post_owner)
        
    # Screen stuff
    opts = ""
    screen.clear()
    screen.border(0)
    screen.addstr(2, 2,"Found files to update: "+'{0}\r'.format(file_count),curses.A_BOLD)
    
    while opts != ord('0'):
            screen.addstr(3, 4,"1 - Backup Remote Site")
            screen.addstr(4, 4,"2 - Synchronize from Local to Remote: ["+localFolder+"/* "+syncsite.prodserver+"]")
            screen.addstr(5, 4,"3 - Restore from a Local backup and synchronize to Remote")
            screen.addstr(6, 4,"0 - Exit the application now")
            screen.addstr(7, 4,"Type a menu option and hit Enter: ",curses.A_BOLD)
            screen.refresh()
            opts = screen.getch()
            if opts == ord('1'):
                write2log("["+syncsite.timestamp+"]: ==================================================================")
                write2log("["+syncsite.timestamp+"]: Creating backup and archive ")
                screen.addstr(10, 4,"Backup remote finished.",curses.A_STANDOUT)
                syncsite.backup2archive()
                screen.refresh()
                write2log("["+baselogstring+"]: ==================================================================")
                #break
            if opts == ord('2'):
                write2log("["+syncsite.timestamp+"]: ==================================================================")
                write2log("["+syncsite.timestamp+"]: Calling rsync remote server ")
                # syncsite.syncsite
                synccommand = ('rsync -rvzhWm --progress --log-file='+logfile+' '+syncsite.exclusions+' '+syncsite.rootfolder+'/* '+syncsite.syncsite)
                screen.addstr(10,4,"Synchronization finished.",curses.A_BOLD)
                # Sync site
                syncsite.p2p_now(synccommand)
                # Change permissions to 0775 and owner back to wwwrun
                PermsOrOwner = syncsite.permsowner(localFolder,'chmod',permissions)
                PermsOrOwner = syncsite.permsowner(localFolder,'chown',pre_owner)
                
                screen.addstr(11,4,"File permissions and ownership on "+localFolder+"/* restored.",curses.A_BOLD)               
                screen.refresh()
                write2log("["+baselogstring+"]: ==================================================================")
                #break
            if opts == ord('3'):
                write2log("["+syncsite.timestamp+"]: ==================================================================")
                write2log("["+syncsite.timestamp+"]: Restoring Backup ")
                archive_lst = syncsite.archivecount()
                arch_lst_stack = archive_lst.split()
                if len(archive_lst) > 0:
                    s = 10
                    fsel = 0
                    for i,tarred in enumerate(archive_lst.split()):
                        fnum = "%i - " %(i+1,)
                        fname = "%s" %(tarred,)
                        screen.addstr(s,4,fnum+fname,curses.A_BOLD)
                        s = s+1
                        i = i+1
                    screen.addstr(s, 4, "0 - Exit")
                    screen.addstr(s+1, 4, "Select backup to restore: ",curses.A_STANDOUT)
                    screen.refresh()
                    fsel = screen.getstr()
                    if fsel != '0': 
                        screen.addstr(s+2,4,"Enter the folder name, relative to ["+localFolder+"] to restore the backup: ",curses.A_BOLD)
                        tmpf = screen.getstr()
                        sX = int(fsel)-1
                        syncsite.restorearchive(arch_lst_stack[sX],tmpf)
                        screen.addstr(s+3,4,syncsite.message)
                        screen.refresh()
                    else:
                        screen.refresh()
                write2log("["+baselogstring+"]: ==================================================================")
                #break
    screen.refresh()
    # send email with all logs!!!
    send_mail(logfile,"techalert@wisekey.com","Finished PUSH2PROD operations for "+syncsite.syncsite,MailServer)
    init_screen('0')

def init_screen(xval):
    global s
    global screen
    global syncsite
    global lFolder
    s = 4
    while xval != ('0'):
        screen = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        screen.clear()
        screen.border(0)
        screen.addstr(2, 2, "[ P2Pv3 : Available Sites ]",curses.A_BOLD)

        for i,conf in enumerate(listFolders.split()):
            menu_string = "%i - " %(i+1,)
            screen.addstr(s, 4, menu_string+conf)
            s = s+1
            i = i+1
        screen.addstr(s, 4, "0 - Exit")
        screen.addstr(s+1, 4, "Type site Number and hit Enter: ",curses.A_STANDOUT)
        screen.refresh()
        xval = screen.getstr()
        
        if xval != '0':
            curses.endwin()
            sX = int(xval)-1
            sconf = listStack[sX]
            sl = len(listStack)
            syncsite = SiteClass(ConfFolder+'/'+sconf,PROD)
            lFolder = syncsite.p2p_root(RootFolder)
            if type(lFolder) is NoneType:
                screen.addstr(sl+7,4,"ERROR:" +sconf+" has not P2P_ROOT variable set. Please correct before using this tool.",curses.color_pair(1))
                screen.addstr(sl+8,4,"Press any key to continue")
                curses.endwin()
                opts = screen.getch()
                init_screen('0')
            else:
               s_options(lFolder)
        else:
            curses.endwin()
            return 0
init_screen(x)
