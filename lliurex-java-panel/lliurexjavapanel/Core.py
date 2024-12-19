#!/usr/bin/env python3
import sys

from . import JavaPanelManager
from . import InstallStack
from . import UninstallStack
from . import SettingsStack
from . import JavaStack
from . import MainStack

class Core:

	singleton=None
	DEBUG=False
	
	@classmethod
	def get_core(self):
		
		if Core.singleton==None:
			Core.singleton=Core()
			Core.singleton.init()

		return Core.singleton


	def __init__(self,args=None):
		
		self.dprint("Init...")
		
	#def __init__
	
	def init(self):

		self.javaPanelManager=JavaPanelManager.JavaPanelManager()
		self.installStack=InstallStack.InstallStack()
		self.unInstallStack=UnInstallStack.UnInstallStack()
		self.settingsStack=SettingsStack.Bridge()
		self.javaStack=JavaStack.Bridge()
		self.mainStack=MainStack.Bridge()

		self.mainStack.initBridge()

	#def init

	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
		

	#def dprint

#class Core
