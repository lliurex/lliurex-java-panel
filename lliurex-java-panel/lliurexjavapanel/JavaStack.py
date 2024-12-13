#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

from . import JavasModel

signal.signal(signal.SIGINT, signal.SIG_DFL)

class Bridge(QObject):


	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.javaPanelManager=self.core.javaPanelManager
		self._javasModel=JavasModel.JavasModel()
		self._enableJavaList=True
		self._uncheckAll=True
		self._filterStatusValue="all"

	#def __init__

	def showInfo(self):

		print("Cargando")
		self._updateJavasModel()
		self.uncheckAll=Bridge.javaPanelManager.uncheckAll
	
	#def showInfo

	def _getUncheckAll(self):

		return self._uncheckAll

	#def _getUncheckAll

	def _setUncheckAll(self,uncheckAll):

		if self._uncheckAll!=uncheckAll:
			self._uncheckAll=uncheckAll
			self.on_uncheckAll.emit()

	#def _setUncheckAll

	def _getEnableJavaList(self):

		return self._enableJavaList

	#def _getEnableJavaList

	def _setEnableJavaList(self,enableJavaList):

		if self._enableJavaList!=enableJavaList:
			self._enableJavaList=enableJavaList
			self.on_enableJavaList.emit()

	#def setEnablePkgList

	def _getJavasModel(self):

		return self._javasModel

	#def _getJavasModel

	def _updateJavasModel(self):

		ret=self._javasModel.clear()
		javasEntries=Bridge.javaPanelManager.javasData
		for item in javasEntries:
			if item["pkg"]!="":
				self._javasModel.appendRow(item["pkg"],item["name"],item["isChecked"],item["status"],item["banner"],item["isVisible"],item["resultProcess"],item["showSpinner"])

	#def _updateJavasModel

	def _getFilterStatusValue(self):

		return self._filterStatusValue

	#def _getFilterStatusValue

	def _setFilterStatusValue(self,filterStatusValue):

		if self._filterStatusValue!=filterStatusValue:
			self._filterStatusValue=filterStatusValue
			self.on_filterStatusValue.emit()

	#def _setFilterStatusValue

	@Slot('QVariantList')
	def onCheckPkg(self,info):

		Bridge.javaPanelManager.onCheckedJavas(info[0],info[1])
		self._refreshInfo()

	#def onCheckPkg

	@Slot()
	def selectAll(self):

		#Bridge.javaPanelManager.selectAll()
		self.filterStatusValue="all"
		self._refreshInfo()
		
	#def selectAll

	def _refreshInfo(self):

		params=[]
		params.append("isChecked")
		self._updateJavasModelInfo(params)
		self.uncheckAll=Bridge.javaPanelManager.uncheckAll
		if len(Bridge.javaPanelManager.javaSelected)>0:
			self.core.mainStack.enableApplyBtn=True
		else:
			self.core.mainStack.enableApplyBtn=False

	#def _refreshInfo
	
	def updateResultJavasModel(self,step,action):

		params=[]
		params.append("showSpinner")
		params.append("resultProcess")
		if step=="start" and action=="install":
			params.append("isVisible")
		if step=="end":
			params.append("banner")
			params.append("status")

		self._updateJavasModelInfo(params)

	#def updateResultJavasModel

	def _updateJavasModelInfo(self,params):

		updatedInfo=Bridge.javaPanelManager.javasData
		if len(updatedInfo)>0:
			for i in range(len(updatedInfo)):
				valuesToUpdate=[]
				index=self._javasModel.index(i)
				for item in params:
					tmp={}
					tmp[item]=updatedInfo[i][item]
					valuesToUpdate.append(tmp)
				self.javasModel.setData(index,valuesToUpdate)
	
	#def _updateJavasModelInfo

	@Slot(str)
	def manageStatusFilter(self,value):

		self.filterStatusValue=value

	#def manageStatusFilter

	on_uncheckAll=Signal()
	uncheckAll=Property(bool,_getUncheckAll,_setUncheckAll,notify=on_uncheckAll)

	on_enableJavaList=Signal()
	enableJavaList=Property(bool,_getEnableJavaList,_setEnableJavaList,notify=on_enableJavaList)
	
	on_filterStatusValue=Signal()
	filterStatusValue=Property(str,_getFilterStatusValue,_setFilterStatusValue,notify=on_filterStatusValue)

	javasModel=Property(QObject,_getJavasModel,constant=True)

#class Bridge

from . import Core

