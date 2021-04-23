#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import configparser
import shutil


BASE_DIR="/usr/share/lliurex-java-panel/"
SWING_FILE=BASE_DIR+"swing.properties"


class javaPanelManager:

	def __init__(self):

		self.core=Core.Core.get_core()
		self.supported_javas=self.core.supported_java
		self.banners=self.core.banners
		self.java_list={}
		self.order=0
		self.result_install={}

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
				if os.path.exists(self.core.banners+info["pkg"]+".png"):
					info["banner"]=self.core.banners+info["pkg"]+".png"
				else:
					info["banner"]=None


				try:
					info["swing"]=config.get("JAVA","swing")
				except Exception as e:
					pass	
				return info
				
		except Exception as e:
			return None

	#def loadFile

	def getSupportedJava(self):

		for item in sorted(os.listdir(self.supported_javas)):
			if os.path.isfile(self.supported_javas+item):
				tmp_info=self.loadFile(self.supported_javas+item)
				if tmp_info!=None:
					tmp_info["installed"]=self.isInstalled(tmp_info["pkg"])

					base_apt_cmd = "apt-cache policy %s "%tmp_info["pkg"]
					p=subprocess.Popen([base_apt_cmd],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
					output=p.communicate()[0]
					if type(output) is bytes:
						output=output.decode()

					if tmp_info["pkg"] not in output:
						available=False
					else:	
						version=output.split("\n")[4]
						if version !='':
							available=True
						else:
							available=False
						
					if available:
						self.java_list[self.order]=tmp_info
						self.order+=1
					
		self.getConfigurationOptions()

	#def getSupportedJava	

	def isInstalled(self,pkg):
		
		p=subprocess.Popen(["dpkg-query -W -f='${db:Status-Status}' %s"%pkg],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output=p.communicate()[0]

		if type(output) is bytes:
			output=output.decode()
		
		if output=="installed":
			return True
			
		return False
		
	#def isInstalled

	def installJava(self,javasToInstall):
	
		cmd=""
		self.result_install={}
		for item in javasToInstall:
			tmp_cmd=self.java_list[item]["cmd"]+";"
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
		
	
		alternative_list=[]
		cpanel_label_list=[]
		cpanel_cmd_list=[]
		self.cpanel_alternatives={}
		
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
from . import Core