#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import configparser
import shutil
import copy
import threading
import urllib.request
import tempfile

import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager


BASE_DIR="/usr/share/lliurex-java-panel/"
SWING_FILE=BASE_DIR+"swing.properties"
PACKAGE_NAME="lliurex-java-panel"

class JavaPanelManager:
	
	ERROR_PARTIAL_INSTALL=-1
	ERROR_INSTALL_INSTALL=-2
	CHANGE_ALTERNATIVE_ERROR=-3
	ERROR_INTERNET_CONNECTION=-4
	ERROR_UNINSTALL_UNINSTALL=-5
	ERROR_PARTIAL_UNINSTALL=-6
	
	SUCCESS_INSTALL_PROCESS=1
	CHANGE_ALTERNATIVE_SUCCESSFULL=2
	SUCCESS_UNINSTALL_PROCESS=7

	MSG_FEEDBACK_INTERNET=3
	MSG_FEEDBACK_INSTALL_REPOSITORIES=4
	MSG_FEEDBACK_INSTALL_INSTALL=5
	MSG_FEEDBACK_UNINSTALL_RUN=6

	def __init__(self):

		self.supportedJavas=os.path.join(BASE_DIR,"supported-javas")
		self.banners=os.path.join(BASE_DIR,"banners")
		self.alternativesBanner="/usr/lib/python3.12/dist-packages/lliurexjavapanel/rsrc"
		self.javasData=[]
		self.javasInfo={}
		self.javaSelected=[]
		self.uncheckAll=False
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
		self.firstConnection=False
		self.secondConnection=False
		self.urltocheck1="http://lliurex.net"
		self.urltocheck2="https://github.com/lliurex"
		self.pkgsInstalled=[]
		self.nonManagedPkg=0
		self.totalPackages=0
		self.javaRegisterDir="/etc/lliurex-java-panel"
		self.javaRegisterFile=os.path.join(self.javaRegisterDir,"managed_java.txt")
		self._clearCache()
		self._createEnvirontment()
		
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
				info["installCmd"]=config.get("JAVA","installCmd")
				info["removeCmd"]=config.get("JAVA","removeCmd")
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

		self._readJavaRegister()

		for item in sorted(os.listdir(self.supportedJavas)):
			if os.path.isfile(os.path.join(self.supportedJavas,item)):
				tmpInfo=self.loadFile(os.path.join(self.supportedJavas,item))
				if tmpInfo!=None:
					status=self.isInstalled(tmpInfo["pkg"])
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
						tmp["status"]=status
						tmp["banner"]=tmpInfo["banner"]
						tmp["showSpinner"]=False
						tmp["isChecked"]=False
						tmp["isVisible"]=True
						tmp["isManaged"]=self.checkIsManaged(tmp["pkg"],status)
						tmp["resultProcess"]=-1
						if status=="installed":
							tmp["banner"]="%s_OK.png"%tmp["banner"]
							if tmp["isManaged"]:
								self.totalPackages+=1
							else:
								self.nonManagedPkg+=1
							self.pkgsInstalled.append(tmp["pkg"])
						else:
							if tmp["isManaged"]:
								self.totalPackages+=1
						self.javasData.append(tmp)
						self.javasInfo[tmpInfo["pkg"]]={}
						self.javasInfo[tmpInfo["pkg"]]["installCmd"]=tmpInfo["installCmd"]
						self.javasInfo[tmpInfo["pkg"]]["removeCmd"]=tmpInfo["removeCmd"]
						self.javasInfo[tmpInfo["pkg"]]["swing"]=tmpInfo["swing"]
						self.javasInfo[tmpInfo["pkg"]]["isManaged"]=tmp["isManaged"]
						self.javasInfo[tmpInfo["pkg"]]["banner"]=tmpInfo["banner"]

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

	def checkIsManaged(self,pkg,status):

		if status=="installed":
			if pkg not in self.registerContent:
				return False
		
		return True 
		
	#def checkIsManaged

	def getConfigurationOptions(self):

		self.configurationData=[]
		self.getCpanelAlternatives()
		self.getJwsAlternatives()
		self.getJreAlternatives()
		self.getFirefoxAlternatives()

	#def getConfigurationOptions	

	def getCpanelAlternatives(self):
	
		self.cPanelAlternatives=[]
		self.cPanelModel=[]
		
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
				tmp["name"]="cpanel"
				tmp["banner"]=os.path.join(self.alternativesBanner,"cpanel.png")
				self.configurationData.append(tmp)

		except Exception as e:
			print(str(e))

	#def getCpanelAlternatives
	
	def getJwsAlternatives(self):
	
		self.jwsAlternatives=[]
		self.jwsModel=[]
		self.jwsCurrentAlternative=0

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
				tmp["name"]="jws"
				tmp["banner"]=os.path.joint(self.alternativesBanner,"jre.png")
				self.configurationData.append(tmp)

		except Exception as e:
			print(str(e))		
								
		try:
			jwsConfiguredCmd='update-alternatives --get-selections | grep javaws$' 
			jwsConfiguredLabel= subprocess.check_output(jwsConfiguredCmd, shell=True)
			if type(jwsConfiguredLabel) is bytes:
				jwsConfiguredLabel=jwsConfiguredLabel.decode()

			jwsCurrentAlternative=jwsConfiguredLabel.split("/")[5].split("\n")[0]	
			for i in range(len(self.jwsAlternatives)):
				if self-jwsAltarnatives[i]["name"]==jwsCurrentAlternative:
					self.jwsCurrentAlternative=i


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
	
			except Exception as e:
				print(str(e))
			
	#def  getJwsAlternatives

	def getJreAlternatives(self):
	
		self.jreAlternatives=[]
		self.jreModel=[]
		self.jreCurrentAlternative=0

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
				tmp["name"]="jre"
				tmp["banner"]=os.path.join(self.alternativesBanner,"jre.png")
				self.configurationData.append(tmp)

		except Exception as e:
			print(str(e))

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
				tmp["name"]="firefox"
				tmp["banner"]=os.path.join(self.alternativesBanner,"firefox.png")					
				self.configurationData.append(tmp)			
		
		except Exception as e:
			print(str(e))		
				
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

	def onCheckedPackages(self,pkgId,isChecked):

		if isChecked:
			self._managePkgSelected(pkgId,True)
		else:
			self._managePkgSelected(pkgId,False)

		if len(self.javaSelected)==self.totalPackages:
			self.uncheckAll=True
		else:
			self.uncheckAll=False

		tmpParam={}
		tmpParam["isChecked"]=isChecked
		
		self._updateJavasModel(tmpParam,pkgId)			
	
	#def onCheckedPackages

	def selectAll(self):

		if self.uncheckAll:
			active=False
		else:
			active=True

		pkgList=copy.deepcopy(self.javasData)
		tmpParam={}
		tmpParam["isChecked"]=active
		for item in pkgList:
			if item["isManaged"]:
				if item["isChecked"]!=active:
					self._managePkgSelected(item["pkg"],active)
					self._updateJavasModel(tmpParam,item["pkg"])
		
		self.uncheckAll=active
		
	#def selectAll

	def _managePkgSelected(self,pkgId,active=True,order=0):

		if active:
			if pkgId not in self.javaSelected:
				self.javaSelected.append(pkgId)
		else:
			if pkgId in self.javaSelected:
				self.javaSelected.remove(pkgId)
		
	#def _managePkgSelected

	def checkInternetConnection(self):

		self.checkingUrl1_t=threading.Thread(target=self._checkingUrl1)
		self.checkingUrl2_t=threading.Thread(target=self._checkingUrl2)
		self.checkingUrl1_t.daemon=True
		self.checkingUrl2_t.daemon=True
		self.checkingUrl1_t.start()
		self.checkingUrl2_t.start()

	#def checkInternetConnection

	def _checkingUrl1(self):

		self.connection=self._checkConnection(self.urltocheck1)
		self.firstConnection=self.connection[0]

	#def _checkingUrl1	

	def _checkingUrl2(self):

		self.connection=self._checkConnection(self.urltocheck2)
		self.secondConnection=self.connection[0]

	#def _checkingUrl2

	def _checkConnection(self,url):
		
		result=[]
		try:
			res=urllib.request.urlopen(url)
			result.append(True)
			
		except Exception as e:
			result.append(False)
			result.append(str(e))
		
		return result	

	#def _checkConnection

	def getResultCheckConnection(self):

 		self.endCheck=False
 		error=False
 		urlError=False
 		self.retConnection=[False,""]

 		if self.checkingUrl1_t.is_alive() and self.checkingUrl2_t.is_alive():
 			pass
 		else:
 			if not self.firstConnection and not self.secondConnection:
 				if self.checkingUrl1_t.is_alive() or self.checkingUrl2_t.is_alive():
 					pass
 				else:
 					self.endCheck=True
 			else:
 				self.endCheck=True

 		if self.endCheck:
 			if not self.firstConnection and not self.secondConnection:
 				error=True
 				msgError=JavaPanelManager.ERROR_INTERNET_CONNECTION
 				self.retConnection=[error,msgError]

	#def getResultCheckConnection

	def initInstallProcess(self):

		self.updateReposLaunched=False
		self.updateReposDone=False

	#def initInstallProcess

	def initPkgInstallProcess(self,pkgId):

		self.installAppLaunched=False
		self.installAppDone=False
		self.checkInstallLaunched=False
		self.checkInstallDone=False
		
		self._initProcessValues(pkgId)

	#def initPkgInstallProcess

	def getUpdateReposCommand(self):

		command="apt-get update"
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"updaterepos")
		else:
			self.updateReposDone=True

		return command

	#def getUpdateReposCommand

	def getInstallCommand(self,pkgId):

		command=""
		command="DEBIAN_FRONTEND=noninteractive %s"%self.javasInfo[pkgId]["installCmd"]
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"install")
		else:
			self.installAppDone=True

		return command

	#def getInstallCommand

	def checkInstall(self,pkgId):

		self.feedBackCheck=[True,"",""]
		self.status=self.isInstalled(pkgId)

		self._updateProcessModelInfo(pkgId,'install',self.status)
		
		if self.status!="installed":
			msgCode=JavaPanelManager.ERROR_INSTALL_INSTALL
			typeMsg="Error"
			self.feedBackCheck=[False,msgCode,typeMsg]
		else:
			msgCode=JavaPanelManager.SUCCESS_INSTALL_PROCESS
			typeMsg="Ok"
			self.copySwingFile(self.javasInfo[pkgId]["swing"])
			self.feedBackCheck=[True,msgCode,typeMsg]
		
		self.checkInstallDone=True

	#def checkInstall

	def copySwingFile(self,destPath):

		if destPath!="":
			destPathSwing=destPath+"swing.properties"
			destPathDiverted=destPathSwing+".diverted"

			try:
				if not os.path.exists(destPathSwing):
					shutil.copy2(SWING_FILE,destPath)
				else:
					if not os.path.exists(destPathDiverted):
						cmdDiversion="dpkg-divert --package "+PACKAGE_NAME+" --add --rename --divert " +destPathDiverted + " "+ destPathSwing
						result=subprocess.check_output(cmdDiversion,shell=True)
						if type(result) is bytes:
							result=result.decode()

						result=result.split("\n")
						if result[0]!="":
							os.symlink(SWING_FILE,destPathSwing)
						else:
							print("Unable to create diversion")
			except Exception as e:
				print("Exception:"+str(e))
				pass

	#def copySwingFile

	def isAllInstalled(self):

		pkgAvailable=0
		if self.totalPackages==len(self.pkgsInstalled):
			return [True,False]
		else:
			pkgAvailable=self.totalPackages-len(self.pkgsInstalled)
			if pkgAvailable==self.totalPackages:
				return [False,True]
			else:
				return [False,False]

	#def isAllInstalled

	def initUnInstallProcess(self,pkgId):

		self.removePkgLaunched=False
		self.removePkgDone=False
		self.checkRemoveLaunched=False
		self.checkRemoveDone=False
		
		self._initProcessValues(pkgId)

	#def initUnInstallProcess

	def _initProcessValues(self,pkgId):

		for item in self.javasData:
			if item["pkg"]==pkgId:
				tmpParam={}
				tmpParam["resultProcess"]=-1
				if item["pkg"] in self.javaSelected:
					tmpParam["showSpinner"]=True
					self._updateJavasModel(tmpParam,item["pkg"])

	#def _initProcessValues

	def getUnInstallCommand(self,pkgId):

		command=""
		command="DEBIAN_FRONTEND=noninteractive %s"%self.javasInfo[pkgId]["removeCmd"]
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"uninstall")
		else:
			self.installAppDone=True

		return command

	#def getUnInstallCommand

	def checkRemove(self,pkgId):

		self.feedBackCheck=[True,"",""]
		self.status=self.isInstalled(pkgId)

		self._updateProcessModelInfo(pkgId,'uninstall',self.status)
		
		if self.status!="available":
			msgCode=JavaPanelManager.ERROR_UNINSTALL_UNINSTALL
			typeMsg="Error"
			self.feedBackCheck=[False,msgCode,typeMsg]
		else:
			msgCode=JavaPanelManager.SUCCESS_UNINSTALL_PROCESS
			typeMsg="Ok"
			self.removeSwingFile(self.javasInfo[pkgId]["swing"])
			self.feedBackCheck=[True,msgCode,typeMsg]
		
		self.checkRemoveDone=True

	#def checkRemove

	def removeSwingFile(self,destPath):

		if destPath!="":
			destPathSwing=destPath+"swing.properties"
			destPathDiverted=destPathSwing+".diverted"

			try:
				if os.path.exists(destPathDiverted):
					if os.path.exists(destPathSwing):
						os.remove(destPathSwing)
					
					cmdDiversion="dpkg-divert --package %s --remove --rename %s"%(PACKAGE_NAME,destPathSwing)
					result=subprocess.check_output(cmdDiversion,shell=True)
					if type(result) is bytes:
						result=result.decode()

					result=result.split("\n")
					if result[0]=="":
						print("Unable to remove diversion")
			
			except Exception as e:
				print("Exception:"+str(e))
				pass

	#def removeSwingFile

	def _updateProcessModelInfo(self,pkgId,action,result):

		for item in self.javasInfo:
			if item==pkgId and item in self.javaSelected:
				tmpParam={}
				if action=="install":
					if result=="installed":
						if pkgId not in self.pkgsInstalled:
							self.pkgsInstalled.append(pkgId)
						tmpParam["resultProcess"]=0
						tmpParam["banner"]="%s_OK"%self.javasInfo[pkgId]["banner"]
					else:
						tmpParam["resultProcess"]=1
				elif action=="uninstall":
					if result=="available":
						if pkgId in self.pkgsInstalled:
							self.pkgsInstalled.remove(pkgId)
						tmpParam["resultProcess"]=0
						tmpParam["banner"]=self.javasInfo[pkgId]["banner"]
					else:
						tmpParam["resultProcess"]=1

				tmpParam["status"]=result
				tmpParam["showSpinner"]=False
				
				self._updateJavasModel(tmpParam,item)
	
	#def _updateProcessModelInfo

	def _updateJavasModel(self,param,pkgId):

		for item in self.javasData:
			if item["pkg"]==pkgId:
				for element in param:
					if item[element]!=param[element]:
						item[element]=param[element]
				break

	#def _updateJavasModel

	def launchAlternativeCommand(self,data):

		if data[0]=="cpanel":
			cmd=self.cPanelAlternatives[data[1]]["cmd"]
		elif data[0]=="jws":
			cmd=self.jwsAlternatives[data[1]]["cmd"]
		elif data[0]=="jre":
			cmd=self.jreAlternatives[data[1]]["cmd"]
		elif data[0]=="firefox":
			cmd=self.firefoxAlternatives[data[1]]["cmd"]

		if data[0]=="cpanel":
			cmd="%s &"%cmd
			os.system(cmd)
			return [True,JavaPanelManager.CHANGE_ALTERNATIVE_SUCCESSFULL]
		else:
			p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
			output=p.communicate()
			rc=p.returncode
			
			self.getConfigurationOptions()

			if rc==0:
				return [True,JavaPanelManager.CHANGE_ALTERNATIVE_SUCCESSFULL]
			else:
				return [False,JavaPanelManager.CHANGE_ALTERNATIVE_ERROR]
		
	
	#def launchAlternativeCommand
	
	def _clearCache(self):

		clear=False
		versionFile="/root/.lliurex-java-panel.conf"
		cachePath1="/root/.cache/lliurex-java-panel"
		installedVersion=self.getPackageVersion()

		try:
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
		except:
			pass

	#def _clearCache

	def getPackageVersion(self):

		packageVersionFile="/var/lib/lliurex-java-panel/version"
		pkgVersion=""

		if os.path.exists(packageVersionFile):
			with open(packageVersionFile,'r') as fd:
				pkgVersion=fd.readline()
				fd.close()

		return pkgVersion

	#def getPackageVersion

	def _createProcessToken(self,command,action):

		cmd=""
		
		if action=="updaterepos":
			self.tokenUpdaterepos=tempfile.mkstemp('_updaterepos')	
			removeTmp=' rm -f %s'%self.tokenUpdaterepos[1]	
		elif action=="install":
			self.tokenInstall=tempfile.mkstemp('_install')
			removeTmp=' rm -f %s'%self.tokenInstall[1]
		elif action=="uninstall":
			self.tokenUnInstall=tempfile.mkstemp('_uninstall')
			removeTmp=' rm -f %s'%self.tokenUnInstall[1]

		cmd='%s ;stty -echo;%s\n'%(command,removeTmp)
		if cmd.startswith(";"):
			cmd=cmd[1:]

		return cmd

	#def _createProcessToken

	def _createEnvirontment(self):

		if not os.path.exists(self.javaRegisterDir):
			os.mkdir(self.javaRegisterDir)
			
		if os.path.exists(self.javaRegisterDir):	
			if not os.path.exists(self.javaRegisterFile):
				with open(self.javaRegisterFile,'w') as fd:
					pass

	#def _createEnvirontment

	def _readJavaRegister(self):

		self.registerContent=[]
		tmpContent=[]
		
		if os.path.exists(self.javaRegisterFile):
			with open(self.javaRegisterFile,'r') as fd:
				tmpContent=fd.readlines()

		for item in tmpContent:
			self.registerContent.append(item.strip())

	#def _updateJavaRegister

	def updateJavaRegister(self):

		for item in self.pkgsInstalled:
			if self.javasInfo[item]["isManaged"]:
				if item not in self.registerContent:
					self.registerContent.append(item)

		if os.path.exists(self.javaRegisterFile):
			with open(self.javaRegisterFile,'w') as fd:
				for item in self.registerContent:
					fd.write("%s\n"%item)

	#def _updateJavaRegister	

#class JavaPanelManager
