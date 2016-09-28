#!/usr/bin/python

import shlex
import sys
import subprocess
from subprocess import check_output, CalledProcessError
from time import gmtime, strftime, sleep
import time
import datetime
import argparse
import os.path
import glob
import sys
import math
import shutil
import urllib2
import webbrowser
import zipfile
import wget

NOT_INSTALLED = 32512
NOT_INSTALLED_WINDOWS = 1
REQUESTING_INSTALL = 256
seedDocsFilePath = './seed_docs/'
glob_helper_id = "com.synchronoss.androidDev.contactcreaterapp"
stdout = open('stdout.txt','wb')
stderr = open('stderr.txt','wb')

Units = ['kb', 'mb', 'gb']
smallSeedFilename = seedDocsFilePath+'50kb.txt'
mediumSeedFilename = seedDocsFilePath+'1mb.txt'
largeSeedFilename = seedDocsFilePath+'30mb.txt'

SeedFiles = {smallSeedFilename : 50, mediumSeedFilename : 1, largeSeedFilename : 30}

def checkAndInstallJavaSDK():
	"""
	Function to check and see if java is installed on the machine, if it is not it will install it and update environment variables.
	"""
	checkOS()
	try:
		status = os.system("java -version")
	except OSError as e:
		print >>sys.stderr, "Error with the command", e

	if (status == NOT_INSTALLED or status == NOT_INSTALLED_WINDOWS or status == REQUESTING_INSTALL):
		print "Java SDK is not installed on this machine."
		cwd = os.getcwd()
		updated = False
		print "JDK does not exist. Downloading it..."
		downloadAndInstallJavaSDK()
		print "Verifying the Java SDK..."
		if verifyInstalled("java -version") == True:
			print "JDK Installation successful"
			return True
		else:
			print "JDK still not installed."
			return False
	else:
		print "Java SDK is already on this machine"
		return True

def downloadAndInstallJavaSDK():
	"""
	Method to download the jdk and set up environment variables
	"""
	print "Downloading Java SDK..."
	if sys.platform=='win32':
		url = "http://download.oracle.com/otn-pub/java/jdk/8u102-b14/jdk-8u102-windows-i586.exe"
		exeFile = wget.download(url)
		print "Download complete."
		folder = extractWindowsFolder(exeFile)
		print "Setting up temp variables..."
		setUpTempVariables(folder)
	else:
		downloadAndInstallMacJavaSDK()
	
def downloadAndInstallMacJavaSDK():
	print "Using homebrew to install java..."
	cmd = "brew cask install java"
	os.system(cmd)
	print "Finished brew installation of java."
	

def extractWindowsFolder(exeFile):
	"""
	Method to run the executable file on windows and extract the jdk into a folder.
	"""
	cwd = os.getcwd()
	print "Extracting jdk from .exe file %s..." % exeFile
	cmd = "%s /s INSTALLDIR=%s/JDK" % (exeFile, cwd)
	os.system(cmd)
	print "Extracted folder from installer."
	folder = cwd + fileSeperator + "JDK"
	print folder
	return folder


def setUpTempVariables(folder):
	"""
	Method to set up the needed environment variables.
	"""
	cwd = os.getcwd()
	cmd = "set path=" + folder + fileSeperator + "bin;%" + "path%"
	print cmd
	os.system(cmd)

def checkOS():
	"""
	Method to adjust the file seperators for file paths.
	"""
	global fileSeperator
	if sys.platform=='win32':
		print "System identified as Windows."
		fileSeperator = "\\"
	else:
		print "System identified as MacOSX."
		fileSeperator = "/"

def checkAndInstallAndroidSDK():
	"""
	Function to check and see if adb is installed on the machine, if it is not it will install it and update environment variables.
	"""
	try:
		status = os.system("adb")
	except OSError as e:
		print >>sys.stderr, "Error with the command", e
	if (status == NOT_INSTALLED or status == NOT_INSTALLED_WINDOWS):
		print "Android SDK is not installed on this machine. Installing..."
		cwd = os.getcwd()
		updated = False
		for i in os.listdir(cwd):
			if (i.lower().find("android-sdk") != -1 and os.path.isdir(i)):
				print "Folder %s exists..." % i
				for j in os.listdir(i):
					if (j.lower().find("platform-tools") != -1):
						print "SDK complete folder already exists. Updating environment variables..."
						setUpEnvironmentVariables(i)
						verifyInstalled("adb")
						updated = True
						break;
				if (updated == False):
					print "SDK folder only partially exists. Installing adb..."
					installADB(i)
					setUpEnvironmentVariables(i)
					verifyInstalled("adb")
					updated = True
					break;
		if (updated == False):
			print "SDK does not exist. Downloading it..."
			downloadAndInstallSDK()
			verifyInstalled("adb")
	else:
		print "Android SDK is installed"

def downloadAndInstallSDK():
	"""
	Method to download the android sdk and set up environment variables
	"""
	if sys.platform=='win32':
		url = "https://dl.google.com/android/android-sdk_r24.4.1-windows.zip"
	else:
		url = "https://dl.google.com/android/android-sdk_r24.4.1-macosx.zip"
	zippedFile = wget.download(url)

	print "Download finished. Unzipping files now..."
	basedir = unzip(zippedFile)
	print "Unzipped complete. Folder %s created" % basedir
	installADB(basedir)
	print "Finished ADB installation..."
	print "Setting up environmental variables..."
	setUpEnvironmentVariables(basedir)


def installADB(basedir):
	"""
	Method to update the sdk to include platform-tools folder
	"""
	checkOS()
	if sys.platform == 'win32':
		cwd = os.getcwd() 
		cmd = cwd + fileSeperator + basedir + fileSeperator + "tools" + fileSeperator + "android.bat update sdk --no-ui -t 1,2,3"
		os.system("echo y | " + cmd)
	else:
		cwd = os.getcwd() 
		cmd = cwd + fileSeperator + basedir + fileSeperator + "tools" + fileSeperator + "android update sdk --no-ui -t 1,2,3"
		sec_cmd = cwd + fileSeperator + basedir + fileSeperator + "tools" + fileSeperator + "android"
		os.chmod(sec_cmd, 0o777)
		os.system("echo y | " + cmd)
	print "Installed ADB."

def setUpEnvironmentVariables(basedir):
	"""
	Method to set up the environment variables
	"""
	if sys.platform == 'win32':
		oldpath = os.environ["PATH"]
		cwd = os.getcwd()
		os.environ["PATH"] = oldpath + ';' + cwd + fileSeperator + basedir + fileSeperator + "platform-tools"
		print os.environ["PATH"]
	else:
		cwd = os.getcwd()
		oldpath = os.environ["PATH"]
		newpath = cwd + fileSeperator + basedir + fileSeperator + "tools:" + fileSeperator + cwd + fileSeperator + basedir + fileSeperator + "platform-tools"
		os.environ["PATH"] = oldpath + fileSeperator + newpath


def verifyInstalled(cmd):
	"""
	Method to check if a command works or not.
	"""
	print "Verifying %s works..." % cmd
	if (sys.platform == 'win32'):
		try:
			status = subprocess.call(shlex.split(cmd))
			print "Installation was successful."
			return True
		except OSError as e:
			print >>sys.stderr, "Execution failed with verification: ",e
			print cmd + " was not installed correctly."
			return False
	else:
		status = os.system(cmd)
		if (status == NOT_INSTALLED):
			print status
			print "An error occured with installation/environment variables. %s is still not installed." % cmd
			return False
		else:
			print "Installation was successful."
			return True

def unzip(zfile, md=False):
	"""
	Method to unzip a compressed file/folder and return the name of it.
	"""
	basedir = ''
	count = -1
	if md:
		basedir = prepareBaseDir(zfile)
	
	zfile = zipfile.ZipFile(zfile, 'r')
	for name in zfile.namelist():
		count+=1
		uname = name.decode('gbk')
		if uname.endswith('.DS_Store'):
			continue
		
		#prepare directory
		dirs = os.path.dirname(uname)
		if basedir:
			dirs = os.path.join(basedir, dirs)
		print 'Extracting: ' + uname
		if dirs and not os.path.exists(dirs):
			print 'Prepare directories: ', dirs
			os.makedirs(dirs)
		if (count == 0):
			homeDir = uname[:-1]
		#ready to unzip file
		data = zfile.read(name)
		if basedir:
			uname = os.path.join(basedir, uname)
		if not os.path.exists(uname):
			fo = open(uname, 'w')
			fo.write(data)
			fo.close()
	zfile.close()
	return homeDir

def docGenerator(docRequirements, docFilePath):
	"""
	Method to generate a specified amount amd size of files
	docRequirements = array of amount, size, and unit
	docFilePath = the destination folder to save docs to.
	"""
	amount = int(docRequirements[0])
	size = docRequirements[1]
	unit = docRequirements[2].lower()
	if not(isValidUnit(unit)):
		print "Unit is incorrect."
		return
	print "Creating %s files, each %s%s in size..." % (amount, size, unit)
	roundDown = int(float(size))
	filename = fileToUse(roundDown, unit)
	numOfWrites = calcNumOfWrites(roundDown, filename, unit)
	for i in range(0, amount):
		for j in range(0, numOfWrites):
			with open(filename) as base:
				with open(docFilePath+"file_%03d.txt" % i, "a") as output:
					output.write(base.read())
		convertedSize = convertFromBytes(int(os.path.getsize(output.name)), unit)
		print "Created file %s of %s%s size." % (output.name, convertedSize, unit)
	print "Generated %s %s%s files locally." % (amount, size, unit)
	base.close()
	pushDocsFromDir(docFilePath)

def calcNumOfWrites(size, seedingFile, currentUnit):
	"""
	Method to calculate the number of writes to a file to generate the specified size.
	"""
	adjust = SeedFiles[seedingFile]
	if (currentUnit == 'gb'):
		size = size * 1024 # convert to mb
	adjust = float(size) / float(adjust)
	return int(math.ceil(adjust))

def convertFromBytes(size, unit):
	"""
	Method to convert the size in bytes into the specified unit.
	size = current size of file in bytes
	unit = units to change size to
	"""
	if (unit == 'kb'):
		return size / 10000
	elif (unit == 'mb'):
		return size / 1000000
	elif (size == 'gb'):
		return size / 1000000000

def isValidUnit(unit):
	"""
	Method to check if the units passed in is valid.
	unit = the unit
	"""
	for i in Units:
		if (unit == i):
			return True;
	return False

def fileToUse(size, unit):
	"""
	Method to determine which size file to use depending on the size of file that needs to be generated.
	size = the size of file needed to generate
	unit = the unit of the size
	"""
	if (unit == 'kb'):
		return smallSeedFilename
	elif (unit == 'mb'):
		if (size < 30):
			return mediumSeedFilename
		else:
			return largeSeedFilename
	elif (unit == 'gb'):
		return largeSeedFilename

def pushDocsFromDir(docDir):
	"""
	Method to push documents/files from a local folder to a phone
	docDir = the filepath of the folder
	"""
	for i in os.listdir(docDir):
		if not(i.endswith(".DS_Store")):
			if not(docDir.endswith("/")):
				filename = (docDir+"/"+i)
			else:
				filename = docDir + i
			pushDocumentToPhone(filename)

	print "Finished pushing files."

def pushDocumentToPhone(file):
	"""
	Method to push a document to a phone
	file = the document/file
	"""
	print "Pushing %s onto target device..." % file
	cmd =r"adb push %s /sdcard/" % file
	os.system(cmd)
	print "Finished pushing %s to phone." % file

def deleteDocumentFromPhone(file):
	"""
	Method to delete a document from a phone
	file = the name of the file to delete
	"""
	print "Removing %s from target device..." % file
	cmd =r"adb shell rm -r %s" % file
	os.system(cmd)
	print "Finished removing file from phone."

def deleteCollectionOfFiles(folderPath):
	"""
	Method to delete a local folder of documents from 
	the phone
	folderPath = path to local folder containing files to delete off phone
	"""
	for i in os.listdir(folderPath):
		deleteDocumentFromPhone("/sdcard/" + i)

def constructSdcardPathFromFolderPath(file):
	"""
	Method to construct the proper URI for sdcard addresses.
	file = the name of the file
	"""
	sdcardPath = "/sdcard" + file[file.rindex('/'):]
	return sdcardPath

def readInCSV(csvFile):
	"""
	Method to pass the csv file into the android helper app
	to read in the contacts.
	csvFile = the name of the .csv file
	"""
	print "Checking if helper app is installed..."
	androidCheckAndInstallHelper()
	try:
		print "Will read in the files from %s" % csvFile
		status = subprocess.call(["adb","shell","am","startservice",
								  "-a", "com.synchronoss.androidDev.contactcreaterapp.action.IMPORT",
								  "-e", "CSV", csvFile,
								  "com.synchronoss.androidDev.contactcreaterapp/.CreateAndAddContacts"],
								 stdout=stdout,stderr=stderr)
		if (status == 1):
			print "Contacts successfully copied from csv on target device."
		if (status != 0):
			print >>sys.stderr, "Unable to launch contact adder app"
			sys.exit()
	except OSError as e:
		print >>sys.stderr, "Execution failed: ", e
		sys.exit()
	waitForHelperApp()

def helperAppCreateContacts(amount):
	"""
	Method to create a specified amount of contacts
	amount = the number of contacts to generate
	"""
	print "Checking if helper app is installed..."
	androidCheckAndInstallHelper()
	try:
		print "Creating " + amount + " contacts and loading onto target device..."
		status = subprocess.call(["adb","shell","am","startservice",
								  "-a", "com.synchronoss.androidDev.contactcreaterapp.action.IMPORT",
								  "-e", "CREATION", amount,
								  "com.synchronoss.androidDev.contactcreaterapp/.CreateAndAddContacts"],
								 stdout=stdout,stderr=stderr)
		if (status == 1):
			print "Contacts successfully created on target device."
		if (status != 0):
			print >>sys.stderr, "Unable to launch contact adder app"
			sys.exit()
	except OSError as e:
		print >>sys.stderr, "Execution failed: ", e
		sys.exit()
	waitForHelperApp()
	

def androidCheckAndInstallHelper():
	"""
	android method to check for the presence of the helper app, and, if not found,
	to install it on the specified device.
	"""
	try:
		device_pkg_list = subprocess.Popen(["adb", "shell", "pm", "list", "packages"],stdout=subprocess.PIPE)
		if (sys.platform == 'win32'):
			status = subprocess.call(["findstr", glob_helper_id], stdin=device_pkg_list.stdout, stdout=stdout,stderr=stderr)
		else:
			status = subprocess.call(["grep","-i",glob_helper_id], stdin=device_pkg_list.stdout,stdout=stdout, stderr=stderr)
	
		if (status is not 0):
			print "Helper app is not installed, installing..."
			androidInstallHelper()
		else:
			print "Helper app is already installed"
	
	except OSError as e:
		print >>sys.stderr, "Execution failed: ",e
		sys.exit(APP_ERROR)

def androidInstallHelper():
	"""
	android method to install the helper app
	"""
	helper_pkg = './android_app/app-debug.apk'

	try:
		status = subprocess.call(["adb", "install", helper_pkg],stdout=stdout,stderr=stderr)
		if (status is not 0):
			print "Unable to install helper app, exiting."
			sys.exit()
	except OSError as e:
		print >>sys.stderr, "Execution failed: ",e
		sys.exit()
	waitForHelperApp()

def waitForHelperApp():
	"""
	Method to wait for helper app to finish any tasks it may be performing
	"""
	status = 0
	count = 0

	try:
		print "Waiting for helper app to complete request"
		
		while (status == 0):
			count += 1
			sleep(5)
			ps_proc = subprocess.Popen(["adb","shell","ps"], stdout=subprocess.PIPE)
			if (sys.platform == 'win32'):
				status = subprocess.call(["findstr", glob_helper_id],
									 stdin=ps_proc.stdout, stdout=stdout,stderr=stderr)
			else:
				status = subprocess.call(["grep", "-i", glob_helper_id],
									 stdin=ps_proc.stdout, stdout=stdout,stderr=stderr)
			if status != 0:
				print "Helper app has completed request"
				break
			elif count > 300:
				print "Helper app has still not completed request, giving up"
				break
	except OSError as e:
		print >> sys.stderr, "Execution failed: ", e
		sys.exit()

def clearContactsFromPhone():
	"""
	Deletes all contacts from an android device.
	"""
	print "Deleting any contacts from phone..."
	cmd =r"adb shell pm clear com.android.providers.contacts"
	os.system(cmd)
	print "Finished deleting contacts from phone."

def clearLocalDir(path):
	"""
	Deletes txt files from a specified folder.
	path = filepath to folder which is to be cleaned.
	"""
	pattern = path + 'file' + '*.txt'
	print "Cleaning up local directory %s of txt files first..." % path
	try:
		for f in glob.glob(pattern):
			os.remove(f)
	except OSError, e:
		print ("Error: %s - %s." % (e.filename,e.strerror))
	print "Finished cleaning local directory"

def mkDir(contentDirPath):
	"""
	Creates a folder.
	contentDirPath = name of folder.
	"""
	if os.path.isdir(contentDirPath):
		print "Directory %s already exists." % contentDirPath
		clearLocalDir(contentDirPath)
		return;
	else:
		os.mkdir(contentDirPath)
		print "Created directory %s." % contentDirPath

def androidDetectDevices():
	"""
	Detects all connected android devices
	
	"""
	devices = []
	try:
		if (sys.platform == 'win32'):
			adb_output = check_output(["adb","devices"])
			if len(adb_output) > 28:
				devices = adb_output
		else:
			adb_output = subprocess.Popen(["adb","devices"], stdout=subprocess.PIPE)
			grep_output = subprocess.check_output(["grep","device"], stdin=adb_output.stdout).splitlines()
			if "List of devices" in grep_output[0] and len(grep_output) > 1:
				devices = [dev.split("\t")[0] for dev in grep_output[1:]]
	except OSError as e:
		print >>sys.stderr, "Execution failed: ", e
		sys.exit()
	return devices

def main():
	print "--- Starting Program ---\n"
	parser = argparse.ArgumentParser(description='Generate contacts')
	parser = argparse.ArgumentParser()
	parser.add_argument("-generate_contacts", help="number of contacts to generate (default 50)")
	parser.add_argument("-csv", help="a filename.csv file containing all contacts to be read in and created.")
	parser.add_argument("-push_docs", help="the name of the folder of the files to push to target device")
	parser.add_argument('-make_docs', nargs = '*', dest = 'numbers', help = 'three arguments 1) the amount docs to create 2) the size of each doc 3) the unit of size eg kb, mb')
	parser.add_argument("-clean_contacts", action="store_true", help="clear all contacts from phone")
	parser.add_argument("-clean_documents", help="clean the documents from a given local file path from a phone")
	args = parser.parse_args()

	if checkAndInstallJavaSDK() == True:
		 checkAndInstallAndroidSDK()
	else:
		sys.exit()

	device_list = androidDetectDevices()
	if (device_list):
		if (len(device_list) > 1):
			print "There is more than one android phone currently connected. Please disconnect one"
			sys.exit()
		else:
			print "Android phone is connected with uuid " + device_list[0]
	else:
		print "No android phone currently connected"
		sys.exit()

	if(args.generate_contacts):
		if(args.generate_contacts == None):
			print "No contact amount specified. Setting amount to 50"
			contactFiles = 50
		elif(args.generate_contacts != None):
			contactFiles=args.generate_contacts
			print "Will generate " + contactFiles + " contacts."
		clearContactsFromPhone()
		helperAppCreateContacts(contactFiles)

	if(args.csv):
		if(args.csv == None):
			print "No .csv file provided"
		elif(args.csv != None):
			csvFile = args.csv
			print "Will use %s for contacts import..." % csvFile
			clearContactsFromPhone()
			pushDocumentToPhone(csvFile)
			phoneFilePath = constructSdcardPathFromFolderPath(csvFile)
			readInCSV(phoneFilePath)
			print "System will now clean phone..."
			deleteDocumentFromPhone(phoneFilePath)

	if(args.push_docs):
		if(args.push_docs == None):
			print "No document directory supplied"
		elif(args.push_docs != None):
			docDir = args.push_docs
			print "Using directory " + docDir + "..."
			pushDocsFromDir(docDir)

	if (args.numbers):
		docRequirements = args.numbers
		if (len(docRequirements) != 3):
			print "Too few/not enough arguments."
		else:
			if (docRequirements[2].isalpha()):
				docFilePath = './etc/'
				mkDir(docFilePath)
				docGenerator(docRequirements, docFilePath)

	if(args.clean_contacts != None and args.clean_contacts):
		print "Deleting contacts..."
		clearContactsFromPhone()

	if (args.clean_documents):
		if(args.clean_documents == None):
			print "No document directory provided"
		elif(args.clean_documents != None):
			docFolder = args.clean_documents
			print "Will clean files from %s from the phone" % docFolder
			deleteCollectionOfFiles(docFolder)
			print "Finished file deletion."

main()