#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script de deploy do RIG BR para Windows (setup .exe) e Linux (pacote .deb)
# Autor: Gustavo Moraes <gustavosotnas1@gmail.com>
# MIT License – Copyright (c) 2018 Gustavo Moraes

import sys, os, json, shutil, subprocess

paths = {
	'manifest': '../manifest.json',
	'build': 'build',
	'dist': 'dist',
	'spec': 'rig-br.spec',
	'pycache': '../src/__pycache__',
	'src': '../src/rig-br.py',
	'icon': '../../rig-br.wiki/icon/rig-br.ico',
	'iscc': 'C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe',
	'iss': '.\\innosetup\\rig-br.iss'
}

# Windows PowerShell Wrapper
class PowerShellWrapper:
	def __encodeCommand__(self, commandString):
		input = 'PowerShell -Command "& {$command = {'+ commandString +'}; $bytes = [System.Text.Encoding]::Unicode.GetBytes($command); $encodedCommand = [Convert]::ToBase64String($bytes); echo $encodedCommand}"'
		output = subprocess.run(input, shell=True, stdout=subprocess.PIPE)
		return output.stdout.decode("utf-8").strip()

	def run(self, command):
		encodedCommand = self.__encodeCommand__(command)
		input = 'PowerShell -encodedCommand "'+ encodedCommand + '"'
		output = subprocess.run(input, shell=True)
		return output

def readManifestFile():
	with open(paths['manifest']) as manifestJSON:
		manifest = json.load(manifestJSON)
	print(manifest)

# Source:
#https://www.webucator.com/how-to/how-check-the-operating-system-with-python.cfm
def getPlatform():
	platforms = {
		'linux1' : 'Linux',
		'linux2' : 'Linux',
		'darwin' : 'OS X',
		'win32' : 'Windows'
	}
	if sys.platform not in platforms:
		return sys.platform
	
	return platforms[sys.platform]

def detectOS():
	osName = getPlatform()
	if osName is "Windows":
		print("OS: Windows")
	elif osName is "Linux":
		print("OS: Linux")
	else:
		print("OS: Unknown ("+ osName +")")

def rm_R(fileOrFolder):
	if os.path.isfile(fileOrFolder):
		try:
			print("Deleting '"+ fileOrFolder +"' file...")
			os.remove(fileOrFolder)
		except OSError as ose:
			print("'"+ fileOrFolder +"' file has been previously deleted.")
	else:
		try:
			print("Deleting '"+ fileOrFolder +"' folder...")
			shutil.rmtree(fileOrFolder)
			print("The folder '"+ fileOrFolder +"' folder has been deleted successfully.")
		except FileNotFoundError as fnfe:
			print("'"+ fileOrFolder +"' folder has been previously deleted.")

def cleanBuild():
	rm_R(paths['build'])
	rm_R(paths['dist'])
	rm_R(paths['spec'])
	rm_R(paths['pycache'])

def isPyinstallerInstalled():
	commandOutput = subprocess.run('pyinstaller --version',
		shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	return True if commandOutput.returncode is 0 else False

def compile():
	commandInput = 'pyinstaller \''+ paths['src'] +'\' -w -i \''+ paths['icon'] +'\''
	if getPlatform() is "Windows":
		# Workaround about PyInstaller (doesn't run in Python shells on Windows)
		commandInput = 'PowerShell -Command "& {'+ commandInput +'}"'
	print(commandInput)
	commandOutput = subprocess.run(commandInput, shell=True)

def isInnoSetupInstalled():
	return True if os.path.isfile(paths['iscc']) else False

def build():
	powershell = PowerShellWrapper()
	powershell.run("& \'" + paths['iscc'] +"\' "+ paths['iss'])

if len(sys.argv) > 1 and sys.argv[1] == '--clean':
	cleanBuild()
else:
	readManifestFile()
	detectOS()
	cleanBuild()
	if isPyinstallerInstalled():
		compile()
	if getPlatform() is "Windows":
		if isInnoSetupInstalled():
			build()
		else:
			print("Build NOT started.")