

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
		RestoreTAR(tarFile,localFolder)
		sendMail("techalert@wisekey.com","Finished PUSH2PROD: restored backup from "+tarFile,MailServer)
	else:
		print "Operation Aborted by user. Exiting now."
		break



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
