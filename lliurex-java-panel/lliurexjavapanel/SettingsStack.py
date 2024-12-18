#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

from . import ConfigurationModel

signal.signal(signal.SIGINT, signal.SIG_DFL)

class ChangeAlternative(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.ret=[]
		self.data=args[0]
		
	#def __init__
		
	def run(self,*args):
		
		self.ret=Bridge.javaPanelManager.launchAlternativeCommand(self.data)

	#def run

#class ChangeAlternative

class Bridge(QObject):

	APPLY_SPACE_CHANGES_MESSAGE=2

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.javaPanelManager=self.core.javaPanelManager
		self._configurationModel=ConfigurationModel.ConfigurationModel()
		self._cPanelModel=Bridge.javaPanelManager.cPanelModel
		self._jwsModel=Bridge.javaPanelManager.jwsModel
		self._jwsCurrentAlternative=Bridge.javaPanelManager.jwsCurrentAlternative
		self._jreModel=Bridge.javaPanelManager.jreModel
		self._jreCurrentAlternative=Bridge.javaPanelManager.jreCurrentAlternative		
		self._firefoxModel=Bridge.javaPanelManager.firefoxModel
		self._firefoxCurrentAlternative=Bridge.javaPanelManager.firefoxCurrentAlternative	
		

	#def __init__

	def getInfo(self):

		self._updateConfigurationModel()
		self.cPanelModel=Bridge.javaPanelManager.cPanelModel
		self.jwsModel=Bridge.javaPanelManager.jwsModel
		self.jwsCurrentAlternative=Bridge.javaPanelManager.jwsCurrentAlternative
		self.jreModel=Bridge.javaPanelManager.jreModel
		self.jreCurrentAlternative=Bridge.javaPanelManager.jreCurrentAlternative		
		self.firefoxModel=Bridge.javaPanelManager.firefoxModel
		self.firefoxCurrentAlternative=Bridge.javaPanelManager.firefoxCurrentAlternative	

	#def showInfo

	def _getCPanelModel(self):

		return self._cPanelModel

	#def _getCPanelModel

	def _setCPanelModel(self,cPanelModel):

		if self._cPanelModel!=cPanelModel:
			self._cPanelModel=cPanelModel
			self.on_cPanelModel.emit()

	#def _setCPanelModel

	def _getJwsModel(self):

		return self._jwsModel

	#def _getJwsModel

	def _setJwsModel(self,jwsModel):

		if self._jwsModel!=jwsModel:
			self._jwsModel=jwsModel
			self.on_jwsModel.emit()

	#def _setCPanelModel

	def _getJwsCurrentAlternative(self):

		return self._jwsCurrentAlternative

	#def _getJwsCurrentAlternative

	def _setJwsCurrentAlternative(self,jwsCurrentAlternative):

		if self._jwsCurrentAlternative!=jwsCurrentAlternative:
			self._jwsCurrentAlternative=jwsCurrentAlternative
			self.on_jwsCurrentAlternative.emit()

	#def _setJwsCurrentAlternative

	def _getJreModel(self):

		return self._jreModel

	#def _getJreMode

	def _setJreModel(self,jreModel):

		if self._jreModel!=jreModel:
			self._jreModel=jreModel
			self.on_jreModel.emit()

	#def _setJreModel

	def _getJreCurrentAlternative(self):

		return self._jreCurrentAlternative

	#def _getJreCurrentAlternative

	def _setJreCurrentAlternative(self,jreCurrentAlternative):

		if self._jreCurrentAlternative!=jreCurrentAlternative:
			self._jreCurrentAlternative=jreCurrentAlternative
			self.on_jreCurrentAlternative.emit()

	#def _setJreCurrentAlternative

	def _getFirefoxModel(self):

		return self._firefoxModel

	#def _getFirefoxModel

	def _setFirefoxModel(self,firefoxModel):

		if self._firefoxModel!=firefoxModel:
			self._firefoxModel=firefoxModel
			self.on_firefoxModel.emit()

	#def _setFirefoxModel

	def _getFirefoxCurrentAlternative(self):

		return self._firefoxCrrentAlternative

	#def _getFirefoxCurrentAlternative

	def _setFirefoxCurrentAlternative(self,firefoxCurrentAlternative):

		if self._firefoxCurrentAlternative!=firefoxCurrentAlternative:
			self._firefoxCurrentAlternative=firefoxCurrentAlternative
			self.on_firefoxCurrentAlternative.emit()

	#def _setFirefoxCurrentAlternative

	def _getConfigurationModel(self):

		return self._configurationModel

	#def _getJavasModel

	def _updateConfigurationModel(self):

		ret=self._configurationModel.clear()
		configurationEntries=Bridge.javaPanelManager.configurationData

		for item in configurationEntries:
			if item["name"]!="":
				self._configurationModel.appendRow(item["name"],item["banner"])
		
		self._configurationModel

	#def _updateConfigurationModel

	@Slot('QVariantList')

	def manageAlternative(self,data):

		launchCommand=True

		if data[0]!="cpanel":
			if data[0]=="jws":
				currentValue=self.jwsCurrentAlternative
			elif data[0]=="jre":
				currentValue=self.jreCurrentAlternative
			elif data[0]=="firefox":
				currentValue=self.firefoxCurrentAlternative

			if data[1]==currentValue:
				launchCommand=False
		
		if launchCommand:
			self.core.mainStack.showStatusMessages=[False,"","Ok"]
			self.core.mainStack.closePopUp=[False,Bridge.APPLY_SPACE_CHANGES_MESSAGE]
			self.core.mainStack.closeGui=False		
			self.changeAlternativeT=ChangeAlternative(data)
			self.changeAlternativeT.start()
			self.changeAlternativeT.finished.connect(self._changeAlternativeRet)
	
	#def manageAlternative

	def _changeAlternativeRet(self):

		self.core.mainStack.closePopUp=[True,""]
		self.core.mainStack.closeGui=True
		if self.changeAlternativeT.ret[0]:
			self.core.mainStack.showStatusMessage=[True,self.changeAlternativeT.ret[1],"Ok"]
		else:
			self.core.mainStack.showStatusMessage=[True,self.changeAlternativeT.ret[1],"Error"]

	#def _changeAlternativeRet


	on_cPanelModel=Signal()
	cPanelModel=Property('QVariant',_getCPanelModel,_setCPanelModel,notify=on_cPanelModel)
	
	on_jwsModel=Signal()
	jwsModel=Property('QVariant',_getJwsModel,_setJwsModel,notify=on_jwsModel)

	on_jwsCurrentAlternative=Signal()
	jwsCurrentAlternative=Property(int,_getJwsCurrentAlternative,_setJwsCurrentAlternative,notify=on_jwsCurrentAlternative)

	on_jreModel=Signal()
	jreModel=Property('QVariant',_getJreModel,_setJreModel,notify=on_jreModel)

	on_jreCurrentAlternative=Signal()
	jreCurrentAlternative=Property(int,_getJreCurrentAlternative,_setJreCurrentAlternative,notify=on_jreCurrentAlternative)

	on_firefoxModel=Signal()
	firefoxModel=Property('QVariant',_getFirefoxModel,_setFirefoxModel,notify=on_firefoxModel)

	on_firefoxCurrentAlternative=Signal()
	firefoxCurrentAlternative=Property(int,_getFirefoxCurrentAlternative,_setFirefoxCurrentAlternative,notify=on_firefoxCurrentAlternative)

	configurationModel=Property(QObject,_getConfigurationModel,constant=True)

#class Bridge

from . import Core

