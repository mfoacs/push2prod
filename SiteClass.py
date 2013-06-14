#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports

import re
import os
import time
import shutil
import curses
import subprocess
import commands
import tarfile

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
        win = curses.initscr()
        #Create a window object.
        win = curses.newwin(3,32,14,10)
        # Add the Border
        win.border(0)
        # Current text: Progress
        win.addstr(1,1,"Progress ")
        # This is to move the progress bar per iteration.
        pos = 10
        # Random number I chose for demonstration.
        for i in range(15):
            # Add '.' for each iteration.
            win.addstr(1,pos,".")
            # Refresh or we'll never see it.
            win.refresh()
            # Here is where you can customize for data/percentage.
            time.sleep(0.05)
            # Need to move up or we'll just redraw the same cell!
            pos += 1
        # Current text: Progress ............... Done!
        win.addstr(1,26,"Done!")
        # Gotta show our changes.
        win.refresh()
        # Without this the bar fades too quickly for this example.
        time.sleep(0.5)
        curses.endwin()
        
    
    def p2p_root(self,pattern):
        'Get the root folder in the Apache conf file'
        self.pattern = pattern
        with open(self.apacheconf) as f:
            for line in f:
                if re.search(self.pattern,line):
                    self.rootfolder = re.search('/.*',line).group()
                    return self.rootfolder

    def p2p_now(self,command):
        'execute a synchronizaton command with the given parameters'
        self.command = command
        #self.progress = self.show_progress()
        return subprocess.call(self.command,shell=True)
        #self.progress
    
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
	self.cmdcount = ('rsync -ravzOn --include .htaccess --progress '+self.exclusions+' '+self.rootfolder+'/* '+self.syncsite)
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
            self.cmdbck = ('rsync -pravzhWm --progress --log-file='+self.logfolder+"/P2P-"+self.filetoday()+'.log '+self.exclusions+' '+self.syncsite+' '+self.snapshots)
        else:
            self.cmdbck = ('rsync -pravzhWm --progress --log-file='+self.logfolder+"/P2P-"+self.filetoday()+'.log '+self.exclusions+' '+self.syncsite+' '+self.snapshots)
        if not os.path.exists(self.archivefolder):
            print "No archive folder found. Creating one..."
            os.makedirs(self.archivefolder)
        self.madeit = self.p2p_now(self.cmdbck)
        self.archived = shutil.make_archive(self.archivefile,'gztar',self.snapshots)
        return self.madeit, self.archived
    
    def archivecount(self):
	"Get the list of backups a site has"
        self.archivefolder = self.rootfolder+"/.archive/"
	self.tarFiles = commands.getoutput('ls '+self.archivefolder)
	return self.tarFiles
    
    def restorearchive(self,archivename,restorepoint):
        "Restore the archive to a TMP directory and deletes the archive file"
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
        return tar, m, self.archivename, self.restorepoint, self.show_progress(), self.message
        
        



flists = ['ddss','sdsd','dfsdf','dssd']
testsite = SiteClass("test.conf","root@vosstg01.wisekey.ch")
print testsite.p2p_root('P2P_ROOT')
print testsite.countfiles()
print testsite.siteversion()
print testsite.cleanup(flists)
print testsite.filetoday()
print testsite.backup2archive()
print testsite.siteversion()
print testsite.prodserver
print testsite.syncsite
print testsite.logfolder
print testsite.archivecount()

sop = testsite.archivecount()
#print sop.split()
print testsite.restorearchive("20121030-15h.tar.gz","TMP")



'''
print "Employee.__doc__:", SiteClass.__doc__
print "Employee.__name__:", SiteClass.__name__
print "Employee.__module__:", SiteClass.__module__
print "Employee.__bases__:", SiteClass.__bases__
print "Employee.__dict__:", SiteClass.__dict__
'''

