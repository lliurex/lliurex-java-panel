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
		self.alternativesBanner="/usr/lib/python3.12/dist-packages/lliurexjavapanel/rsrc"
		self.javasData=[]
		self.javasInfo={}
		self.javaSelected=[]
		self.uncheckAll=True
		self.configurationData=[]
		self.cPanelAlternatives=[]
		self.cPanelModel=[]
		self.jwsAlternatives=[]
		self.jwsModel=[]
		self.jwsCurrentAlternative=0
		self.jreAlternatives=[]
		self.jreModel=[]
		self.jreCurrentAlternative=0
		self.firefoxAlternatives=[]
		self.firefoxModel=[]
		self.firefoxCurrentAlternative=0
		self.clearCache()
		
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
					
		self.getConfigurationOptions()

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
	'''
	def getConfigurationOptions(self):

		self.getCpanelAlternatives()
		self.getJwsAlternatives()
		self.getJreAlternatives()
		self.getFirefoxAlternatives()

	#def getConfigurationOptions	

	def getCpanelAlternatives(self):
		
	
		self.cPanelAlternatives=[]
		self.cPanelModel=[]
		
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

			if type(javaLabelOutput) is bytes:
				javaLabelOutput=javaLabelOutput.decode()

			javaLabelOutput=javaLabelOutput.split("\n")

			i=0
			for item in javaLabelOutput:
			
				if javaLabelOutput[i]!='':
					if ('openjdk' not in javaLabelOutput[i]):
						tmp={}
						tmp["name"]=item
						tmp["cmd"]=javaCmdList[i].replace("bin/java", "bin/jcontrol")
						self.cPanelAlternatives.append(tmp)
						self.cPanelModel.append(item)
					
					i+=1

			if len(self.cPanelAlternatives)>0:
				tmp={}
				tmp["id"]=1
				tmp["banner"]=os.path.join(self.alternativesBanner,"cpanel.png")
				self.configurationData.append(tmp)

		except Exception as e:
			print(str(e))

	#def getCpanelAlternatives
	
	def getJwsAlternatives(self):
	
		self.jwsAlternatives=[]
		self.jwsModel=[]
		self.jwsCurrentAlternative=0

		# build alternatives list here
		
		# ############### #
		try:
			javaCmd='update-alternatives --list javaws | grep -v "gij"'
			javaCmdList=subprocess.check_output(javaCmd, shell=True)

			if type(javaCmdList) is bytes:
				javaCmdList=javaCmdList.decode()

			javaCmdList=javaCmdList.split("\n")

			javaLabel='update-alternatives --list javaws | grep -v "gij" | cut -d"/" -f5'
			javaLabelList=subprocess.check_output(javaLabel, shell=True)


			if type(javaLabelList) is bytes:
				javaLabelList=javaLabelList.decode()

			javaLabelList=javaLabelList.split("\n")
			

			i=0
			for item in javaLabelList:
				if javaLabelList[i]!='':
					tmp={}
					tmp["name"]=item
					tmp["cmd"]='update-alternatives --set javaws ' + javaCmdList[i]
					self.jwsAlternatives.append(tmp)
					self.jwsModel.append(item)
					i+=1
			if len(self.jwsAlternatives)>0:
				tmp={}
				tmp["id"]=2
				tmp["banner"]=os.path.joint(self.alternativesBanner,"jre.png")
				self.configurationData.append(tmp)

		except Exception as e:
			print(str(e))		
								
		# get jws configured actually
		
		# ################ #
		try:
			jwsConfiguredCmd='update-alternatives --get-selections | grep javaws$' 
			jwsConfiguredLabel= subprocess.check_output(jwsConfiguredCmd, shell=True)
			if type(jwsConfiguredLabel) is bytes:
				jwsConfiguredLabel=jwsConfiguredLabel.decode()

			jwsCurrentAlternative=jwsConfiguredLabel.split("/")[5].split("\n")[0]	
			for i in range(len(self.jwsAlternatives)):
				if self-jwsAltarnatives[i]["name"]==jwsCurrentAlternative:
					self.jwsCurrentAlternative=i

			#self.jws_alternatives[jws_configured_label]["default"]=True
		
		except Exception as e:
			print(str(e))
			try:
				jwsRemove=subprocess.check_output(jwsConfiguredCmd, shell=True)
				if type(jwsRemove) is bytes:
					jwsRemove=jwsRemove.decode()
				
				jwsRemove=jwsRemove.split()[2]
				removeAlternative='update-alternatives --remove "javaws"' + ' "'+ jwsRemove+'"'
				
				os.system(removeAlternative)
				
				jwsConfiguredCmd='update-alternatives --get-selections |grep javaws$' 
				jwsConfiguredLabel= subprocess.check_output(jwsConfiguredCmd, shell=True)

				if type(jwsConfiguredLabel) is bytes:
					jwsConfiguredLabel=jwsConfiguredLabel.decode()

				jwsCurrentAlternative=jwsConfiguredLabel.split("/")[4]	
				for i in range(len(self.jwsAlternatives)):
					if self-jwsAltarnatives[i]["name"]==jwsCurrentAlternative:
						self.jwsCurrentAlternative=i
			
				#self.jws_alternatives[jws_configured_label]["default"]=True
			
			except Exception as e:
				print(str(e))
			
	
		
	#def  getJwsAlternatives

	def getJreAlternatives(self):
	
		self.jreAlternatives=[]
		self.jreModel=[]
		self.jreCurrentAlternative=0
		# build alternatives list here
		
		# ############### #
		try:	
			javaCmd='update-alternatives --list java | grep -v "gij"'
			javaCmdList=subprocess.check_output(javaCmd, shell=True)

			if type(javaCmdList) is bytes:
				javaCmdList=javaCmdList.decode()

			javaCmdList=javaCmdList.split("\n")


			javaLabel='update-alternatives --list java | grep -v "gij" | cut -d"/" -f5'
			javaLabelList=subprocess.check_output(javaLabel, shell=True)

			if type(javaLabelList) is bytes:
				javaLabelList=javaLabelList.decode()

			javaLabelList=javaLabelList.split("\n")


			i=0
			for item in javaLabelList:
				if javaLabelList[i]!='':
					tmp={}
					tmp["name"]=item
					tmp["cmd"]='update-alternatives --set java ' + javaCmdList[i]
					self.jreAlternatives.append(tmp)
					self.jreModel.append(item)
					i+=1
				
			if len(self.jreAlternatives)>0:
				tmp={}
				tmp["id"]=3
				tmp["banner"]=os.path.join(self.alternativesBanner,"jre.png")
				self.configurationData.append(tmp)

		except Exception as e:
			print(str(e))
		# get jre configured actually
		
		# ################ #
		try:
			jreConfiguredCmd='update-alternatives --get-selections |grep java$' 
			jreConfiguredLabel=subprocess.check_output(jreConfiguredCmd, shell=True)

			if type(jreConfiguredLabel) is bytes:
				jreConfiguredLabel=jreConfiguredLabel.decode()

			jreConfiguredLabel=jreConfiguredLabel.split("/")[4]	
			for i in range(len(self.jreAlternatives)):
				if self.jreAlternatives[i]["name"]==jreConfiguredLabel:
					self.jreCurrentAlternative=i

		except Exception as e:
			print(str(e))
		

	#def getJreAlternatives

	def getFirefoxAlternatives(self):
	
		self.firefoxAlternatives=[]
		self.firefoxModel=[]
		self.firefoxCurrentAlternative=0
		
		# build alternatives list here
		
		# ############### #
		try:
			javaPluginCmd='update-alternatives --list mozilla-javaplugin.so | grep -v "gij"' 
			javaPluginCmdList=subprocess.check_output(javaPluginCmd, shell=True)

			if type(javaPluginCmdList) is bytes:
				javaPluginCmdList=javaPluginCmdList.decode()

			javaPluginCmdList=javaPluginCmdList.split("\n")

			javaPluginLabel='update-alternatives --list mozilla-javaplugin.so | grep -v "gij" | cut -d"/" -f5'
			javaPluginLabelList=subprocess.check_output(javaPluginLabel, shell=True)

			if type(javaPluginLabelList) is bytes:
				javaPluginLabelList=javaPluginLabelList.decode()

			javaPluginLabelList=javaPluginLabelList.split("\n")

			i=0
			for item in javaPluginLabelList:
				if javaPluginLabelList[i]!='':
					tmp={}
					tmp["name"]=item
					tmp["cmd"]='update-alternatives --set mozilla-javaplugin.so ' + javaPluginCmdList[i]
					self.firefoxAlternatives.append(tmp)
					self.firefoxModel.append(item)
					i+=1
			
			if len(self.firefoxAlternatives)>0:
				tmp={}
				tmp["id"]=4
				tmp["banner"]=os.path.join(self.alternativesBanner,"firefox.png")					
				self.configurationData.append(tmp)			
		
		except Exception as e:
			print(str(e))		
				
					
		# get mozilla plugin configured actually
		
		# ################ #
		try:
			firefoxConfiguredCmd='update-alternatives --get-selections |grep mozilla-javaplugin.so' 
			firefoxConfiguredLabel=subprocess.check_output(firefoxConfiguredCmd, shell=True)
			
			if type(firefoxConfiguredLabel) is bytes:
				firefoxConfiguredLabel=firefoxConfiguredLabel.decode()

			firefoxConfiguredLabel=firefoxConfiguredLabel.split("/")[4]	
			for i in range(len(self.firefoxAlternatives)):
				if self.firefoxAlternatives[i]["name"]==firefoxConfiguredLabel:
					self.firefoxCurrentAlternative=i

		except Exception as e:
			print(str(e))	
		
		
	#def  getFirefoxAlternatives
	
	def launchAlternativeCommand(self,data):

		if data[0]==1:
			cmd=self.cPanelAlternatives[data[1]]["cmd"]
		elif data[0]==2:
			cmd=self.jwsAlternatives[data[1]]["cmd"]
		elif data[0]==3:
			cmd=self.jreAlternatives[data[1]]["cmd"]
		elif data[0]==4:
			cmd=self.firefoxAlternatives[data[1]]["cmd"]

		print(cmd)
		'''
		os.system(cmd)
		self.getConfigurationOptions()
		'''

	#def launchAlternativeCommand
	'''
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

	def clearCache(self):

		clear=False
		versionFile="/root/.lliurex-java-panel.conf"
		cachePath1="/root/.cache/lliurex-java-panel"
		installedVersion=self.getPackageVersion()

		if not os.path.exists(versionFile):
			with open(versionFile,'w') as fd:
				fd.write(installedVersion)
				fd.close()

			clear=True

		else:
			with open(versionFile,'r') as fd:
				fileVersion=fd.readline()
				fd.close()

			if fileVersion!=installedVersion:
				with open(versionFile,'w') as fd:
					fd.write(installedVersion)
					fd.close()
				clear=True
		
		if clear:
			if os.path.exists(cachePath1):
				shutil.rmtree(cachePath1)

	#def clearCache

	def getPackageVersion(self):

		packageVersionFile="/var/lib/lliurex-java-panel/version"
		pkgVersion=""

		if os.path.exists(packageVersionFile):
			with open(packageVersionFile,'r') as fd:
				pkgVersion=fd.readline()
				fd.close()

		return pkgVersion

	#def getPackageVersion

#class JavaPanelManager
