#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import configparser
import shutil
import copy
import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager


BASE_DIR="/usr/share/lliurex-java-panel/"
SWING_FILE=BASE_DIR+"swing.properties"
PACKAGE_NAME="lliurex-java-panel"

class JavaPanelManager:

	def __init__(self):

		self.supportedJavas=os.path.join(BASE_DIR,"supported-javas")
		self.banners=os.path.join(BASE_DIR,"banners")
		self.javasData=[]
		self.javasInfo={}
		self.javaSelected=[]
		self.uncheckAll=True
		
	#def __init__
	
	def loadFile(self,path):

		try:
			config = configparser.ConfigParser()
			config.optionxform=str
			config.read(path)
			if config.has_section("JAVA"):
				info={}
				info["pkg"]=config.get("JAVA","pkg")
				info["name"]=config.get("JAVA","name")
				info["cmd"]=config.get("JAVA","cmd")
				if os.path.exists(os.path.join(self.banners,info["pkg"]+".png")):
					info["banner"]=os.path.join(self.banners,info["pkg"]+".png")
				else:
					info["banner"]=None
				try:
					info["swing"]=config.get("JAVA","swing")
				except Exception as e:
					info["swing"]=""
					pass	
				return info
				
		except Exception as e:
			return None

	#def loadFile

	def getSupportedJava(self):

		for item in sorted(os.listdir(self.supportedJavas)):
			if os.path.isfile(os.path.join(self.supportedJavas,item)):
				tmpInfo=self.loadFile(os.path.join(self.supportedJavas,item))
				if tmpInfo!=None:
					javaInstalled=self.isInstalled(tmpInfo["pkg"])
					baseAptCmd = "apt-cache policy %s "%tmpInfo["pkg"]
					p=subprocess.Popen([baseAptCmd],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
					output=p.communicate()[0]
					if type(output) is bytes:
						output=output.decode()

					if tmpInfo["pkg"] not in output:
						available=False
					else:	
						version=output.split("\n")[4]
						if version !='':
							available=True
						else:
							available=False
						
					if available:
						tmp={}
						tmp["pkg"]=tmpInfo["pkg"]
						tmp["name"]=tmpInfo["name"]
						tmp["status"]=javaInstalled
						tmp["banner"]=tmpInfo["banner"]
						tmp["showSpinner"]=False
						tmp["isChecked"]=False
						tmp["isVisible"]=True
						if javaInstalled=="installed":
							tmp["resultProcess"]=0
						else:
							tmp["resultProcess"]=-1
						self.javasData.append(tmp)
						self.javasInfo[tmpInfo["pkg"]]={}
						self.javasInfo[tmpInfo["pkg"]]["cmd"]=tmpInfo["cmd"]
						self.javasInfo[tmpInfo["pkg"]]["swing"]=tmpInfo["swing"]
					
		#self.getConfigurationOptions()

	#def getSupportedJava	
	
	def isInstalled(self,pkg):
		
		p=subprocess.Popen(["dpkg-query -W -f='${db:Status-Status}' %s"%pkg],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output=p.communicate()[0]

		if type(output) is bytes:
			output=output.decode()
		
		if output=="installed":
			return "installed"
			
		return "available"
		
	#def isInstalled
	'''
	def installJava(self,javasToInstall):
	
		cmd="DEBIAN_FRONTEND=noninteractive apt-get install -y "
		self.result_install={}
		for item in javasToInstall:
			tmp_cmd=self.java_list[item]["pkg"]+" "
			cmd=cmd+tmp_cmd
		
		os.system(cmd)

		self.getConfigurationOptions()
		for item in javasToInstall:
			self.result_install[item]=self.isInstalled(self.java_list[item]["cmd"].split("-y")[1].strip())	
			self.copySwingFile(self.java_list[item]["swing"])

		

	def copySwingFile(self,destPath):

		destPath_swing=destPath+"swing.properties"
		destPath_diverted=destPath_swing+".diverted"

		try:
			if not os.path.exists(destPath_swing):
				shutil.copy2(SWING_FILE,destPath)
			else:

				if not os.path.exists(destPath_diverted):
					cmd_diversion="dpkg-divert --package "+PACKAGE_NAME+" --add --rename --divert " +destPath_diverted + " "+ destPath_swing
					result=subprocess.check_output(cmd_diversion,shell=True)
					if type(result) is bytes:
						result=result.decode()

					result=result.split("\n")
					if result[0]!="":
						os.symlink(SWING_FILE,destPath_swing)
					else:
						print("Unable to create diversion")
		except Exception as e:
			print("Exception:"+str(e))
			pass

	#def copySwingFile

	def getConfigurationOptions(self):

		self.getCpanelAlternatives()
		self.getJwsAlternatives()
		self.getJreAlternatives()
		self.getFirefoxAlternatives()

	#def getConfigurationOptions	

	def getCpanelAlternatives(self):
		
	
		alternativeList=[]
		cpanelLabelList=[]
		cpanelCmdList=[]
		self.cpanelAlternatives=[]
		self.cpanelAlternativesName=[]
		
		# build alternatives list here
		
		# ############### #
		try:		
			javaCmd='update-alternatives --list java | grep -v "gij"'
			javaCmdList=subprocess.check_output(javaCmd, shell=True)

			if type(javaCmdList) is bytes:
				javaCmdList=javaCmdList.decode()
			
			javaCmdList=javaCmdList.split("\n")
			javaLabel='update-alternatives --list java | grep -v "gij" | cut -d"/" -f5'
			javaLabelOutput=subprocess.check_output(javaLabel, shell=True)

			if type(javaLabel_list) is bytes:
				java_label_list=java_label_list.decode()

			java_label_list=java_label_list.split("\n")

			i=0
			for item in java_label_list:
			
				if java_label_list[i]!='':
					if ('openjdk' not in java_label_list[i]):
						cpanel_label_list.append(item)
						cpanel_cmd_list.append(java_cmd_list[i].replace("bin/java", "bin/jcontrol"))
						self.cpanel_alternatives[item]={}
						self.cpanel_alternatives[item]["cmd"]=java_cmd_list[i].replace("bin/java", "bin/jcontrol")
					i+=1
			
			
		except Exception as e:
			print(str(e))

	#def getCpanelAlternatives
	
	def getJwsAlternatives(self):
	
		
		alternative_list=[]
		jws_label_list=[]
		jws_cmd_list=[]
		self.jws_alternatives={}
		# build alternatives list here
		
		# ############### #
		try:
			java_cmd='update-alternatives --list javaws | grep -v "gij"'
			java_cmd_list=subprocess.check_output(java_cmd, shell=True)

			if type(java_cmd_list) is bytes:
				java_cmd_list=java_cmd_list.decode()

			java_cmd_list=java_cmd_list.split("\n")

			java_label='update-alternatives --list javaws | grep -v "gij" | cut -d"/" -f5'
			java_label_list=subprocess.check_output(java_label, shell=True)


			if type(java_label_list) is bytes:
				java_label_list=java_label_list.decode()

			java_label_list=java_label_list.split("\n")
			

			i=0
			for item in java_label_list:
				if java_label_list[i]!='':
					jws_label_list.append(item)
					jws_cmd_list.append('update-alternatives --set javaws ' + java_cmd_list[i])
					self.jws_alternatives[item]={}
					self.jws_alternatives[item]["cmd"]='update-alternatives --set javaws ' + java_cmd_list[i]
					self.jws_alternatives[item]["default"]=False
					i+=1
		
		except Exception as e:
			print(str(e))		
								
		# get jws configured actually
		
		# ################ #
		try:
			jws_configured_cmd='update-alternatives --get-selections | grep javaws$' 
			jws_configured_label= subprocess.check_output(jws_configured_cmd, shell=True)
			if type(jws_configured_label) is bytes:
				jws_configured_label=jws_configured_label.decode()

			jws_configured_label=jws_configured_label.split("/")[5].split("\n")[0]	
			self.jws_alternatives[jws_configured_label]["default"]=True
		
		except Exception as e:
			print(str(e))
			try:
				jws_remove=subprocess.check_output(jws_configured_cmd, shell=True)
				if type(jws_remove) is bytes:
					jws_remove=jws_remove.decode()
				
				jws_remove=jws_remove.split()[2]
				remove_alternative='update-alternatives --remove "javaws"' + ' "'+ jws_remove+'"'
				
				os.system(remove_alternative)
				
				jws_configured_cmd='update-alternatives --get-selections |grep javaws$' 
				jws_configured_label= subprocess.check_output(jws_configured_cmd, shell=True)

				if type(jws_configured_label) is bytes:
					jws_configured_label=jws_configured_label.decode()

				jws_configured_label=jws_configured_label.split("/")[4]	
				self.jws_alternatives[jws_configured_label]["default"]=True
			
			except Exception as e:
				print(str(e))
			
	
		
	#def  getJwsAlternatives

	def getJreAlternatives(self):
	
		alternative_list=[]
		jre_label_list=[]
		jre_cmd_list=[]
		self.jre_alternatives={}
		# build alternatives list here
		
		# ############### #
		try:	
			java_cmd='update-alternatives --list java | grep -v "gij"'
			java_cmd_list=subprocess.check_output(java_cmd, shell=True)

			if type(java_cmd_list) is bytes:
				java_cmd_list=java_cmd_list.decode()

			java_cmd_list=java_cmd_list.split("\n")


			java_label='update-alternatives --list java | grep -v "gij" | cut -d"/" -f5'
			java_label_list=subprocess.check_output(java_label, shell=True)

			if type(java_label_list) is bytes:
				java_label_list=java_label_list.decode()

			java_label_list=java_label_list.split("\n")


			i=0
			for item in java_label_list:
				if java_label_list[i]!='':
					jre_label_list.append(item)
					jre_cmd_list.append('update-alternatives --set java ' + java_cmd_list[i])
					self.jre_alternatives[item]={}
					self.jre_alternatives[item]["cmd"]='update-alternatives --set java ' + java_cmd_list[i]
					self.jre_alternatives[item]["default"]=False
					i+=1
				
					
		except Exception as e:
			print(str(e))
		# get jre configured actually
		
		# ################ #
		try:
			jre_configured_cmd='update-alternatives --get-selections |grep java$' 
			jre_configured_label=subprocess.check_output(jre_configured_cmd, shell=True)

			if type(jre_configured_label) is bytes:
				jre_configured_label=jre_configured_label.decode()

			jre_configured_label=jre_configured_label.split("/")[4]	
			self.jre_alternatives[jre_configured_label]["default"]=True
		

		except Exception as e:
			print(str(e))
		

	#def getJreAlternatives

	def getFirefoxAlternatives(self):
	
		alternative_list=[]
		firefox_label_list=[]
		firefox_cmd_list=[]	
		self.firefox_alternatives={}
		
		# build alternatives list here
		
		# ############### #
		try:
			javaplugin_cmd='update-alternatives --list mozilla-javaplugin.so | grep -v "gij"' 
			javaplugin_cmd_list=subprocess.check_output(javaplugin_cmd, shell=True)

			if type(javaplugin_cmd_list) is bytes:
				javaplugin_cmd_list=javaplugin_cmd_list.decode()

			javaplugin_cmd_list=javaplugin_cmd_list.split("\n")


			javaplugin_label='update-alternatives --list mozilla-javaplugin.so | grep -v "gij" | cut -d"/" -f5'
			javaplugin_label_list=subprocess.check_output(javaplugin_label, shell=True)

			if type(javaplugin_label_list) is bytes:
				javaplugin_label_list=javaplugin_label_list.decode()

			javaplugin_label_list=javaplugin_label_list.split("\n")

			i=0
			for item in javaplugin_label_list:
				if javaplugin_label_list[i]!='':
					firefox_label_list.append(item)
					firefox_cmd_list.append('update-alternatives --set mozilla-javaplugin.so ' + javaplugin_cmd_list[i])
					self.firefox_alternatives[item]={}
					self.firefox_alternatives[item]["cmd"]='update-alternatives --set mozilla-javaplugin.so ' + javaplugin_cmd_list[i]
					self.firefox_alternatives[item]["default"]=False
					i+=1
							
		except Exception as e:
			print(str(e))		
				
					
		# get mozilla plugin configured actually
		
		# ################ #
		try:
			firefox_configured_cmd='update-alternatives --get-selections |grep mozilla-javaplugin.so' 
			firefox_configured_label=subprocess.check_output(firefox_configured_cmd, shell=True)
			
			if type(firefox_configured_label) is bytes:
				firefox_configured_label=firefox_configured_label.decode()

			firefox_configured_label=firefox_configured_label.split("/")[4]	
			self.firefox_alternatives[firefox_configured_label]["default"]=True
			
		
		except Exception as e:
			print(str(e))	
		
		
	#def  getFirefoxAlternatives

	def alternativeCommand(self,cmd):

		os.system(cmd)
		self.getConfigurationOptions()

	def getNumberPackages(self,javasToInstall):

		pkgs=""
		for item in javasToInstall:
			pkgs=pkgs+" "+self.java_list[item]["pkg"]
		
		cmd="LANG=C LANGUAGE=en apt-get update; apt-get install --simulate %s"%pkgs
		psimulate = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		rawoutputpsimulate = psimulate.stdout.readlines()
		rawpackagestoinstall = [ aux.decode().strip() for aux in rawoutputpsimulate if aux.decode().startswith('Inst') ]
		r = [ aux.replace('Inst ','') for aux in rawpackagestoinstall ]
		for allinfo in r :
			self.initialNumberPackages.append(allinfo.split(' ')[0])

		self.numberPackagesUnpacked=copy.deepcopy(self.initialNumberPackages)
		self.numberPackagesInstalled=copy.deepcopy(self.initialNumberPackages)

	#def getNumberPackages

	def isAptRunning(self):

		locks_info=self.dpkgUnlocker.isDpkgLocked()
		if locks_info==3:
			return True
		else:
			return False

	#def isAptRunning

	def checkProgressUnpacked(self):

		for i in range(len(self.numberPackagesUnpacked)-1,-1,-1):
			status=self.checkStatus(self.numberPackagesUnpacked[i])
			if status==1:
				self.numberPackagesUnpacked.pop(i)
			elif status==0:
				self.numberPackagesUnpacked.pop(i)
				self.numberPackagesInstalled.pop(i)	

		self.progressUnpacked=len(self.initialNumberPackages)-len(self.numberPackagesUnpacked)
		self.progressUnpackedPercentage="{:.2f}".format(1-float(len(self.numberPackagesUnpacked)/len(self.initialNumberPackages)))
	#def checkProgressUnpacked

	def checkProgressInstallation(self):

		for i in range(len(self.numberPackagesInstalled)-1,-1,-1):
			status=self.checkStatus(self.numberPackagesInstalled[i])
			if status==0:
				self.numberPackagesInstalled.pop(i)

		self.progressInstallation=len(self.initialNumberPackages)-len(self.numberPackagesInstalled)
		self.progressInstallationPercentage="{:.2f}".format(1-float(len(self.numberPackagesInstalled)/len(self.initialNumberPackages)))
	
	#def checkProgressInstallation
	
	def checkStatus(self,pkg):
		
		p=subprocess.Popen(["dpkg-query -W -f='${db:Status-Status}' %s"%pkg],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output=p.communicate()[0]

		if type(output) is bytes:
			output=output.decode()
		
		if output=="installed":
			return 0

		elif output=="unpacked":
			return 1
		
		return -1
	
	#def checkStatus
	'''
#class JavaPanelManager