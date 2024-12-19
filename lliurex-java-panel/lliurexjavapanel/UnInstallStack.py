#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

signal.signal(signal.SIGINT, signal.SIG_DFL)

class UnInstallStack(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		UnInstallStack.javaPanelManager=self.core.javaPanelManager

	#def __init__

	def unInstallProcess(self):

		UnInstallStack.javaPanelManager.totalUninstallError=0
		self.core.javaStack.totalErrorInProcess=UnInstallStack.javaPanelManager.totalUninstallError
		self.endAction=False
		self.pkgProcessed=False
		self.error=False
		self.totalError=0
		self.showError=False
		countLimit=len(UnInstallStack.javaPanelManager.javaSelected)
		if countLimit==0:
			self.countLimit=1
		else:
			self.countLimit=countLimit

		self.pkgToSelect=-1
		self.pkgToProcess=""
		self.uninstallProcessTimer=QTimer(None)
		self.uninstallProcessTimer.timeout.connect(self._uninstallProcessTimerRet)
		self.uninstallProcessTimer.start(100)		

	#def _checkMetaProtectionRet

	def _uninstallProcessTimerRet(self):

		if not self.pkgProcessed:
			if not self.endAction:
				self.pkgToSelect+=1
				if self.pkgToSelect<self.countLimit:
					self.pkgToProcess=UnInstallStack.javaPanelManager.javaSelected[self.pkgToSelect]
					UnInstallStack.javaPanelManager.initUnInstallProcess(self.pkgToProcess)
					self.core.javaStack.updateResultJavasModel('start')
					if not UnInstallStack.javaPanelManager.removePkgLaunched:
						UnInstallStack.javaPanelManager.removePkgLaunched=True
						self.core.mainStack.currentCommand=UnInstallStack.javaPanelManager.getUnInstallCommand(self.pkgToProcess)
						self.core.mainStack.endCurrentCommand=True
				else:
					self.endAction=True

				self.pkgProcessed=True

		if not self.endAction:
			if UnInstallStack.javaPanelManager.removePkgDone:
				if not UnInstallStack.javaPanelManager.checkRemoveLaunched:
					UnInstallStack.javaPanelManager.checkRemoveLaunched=True
					UnInstallStack.javaPanelManager.checkRemove(self.pkgToProcess)

				if UnInstallStack.javaPanelManager.checkRemoveDone:
					self.core.javaStack.updateResultJavasModel("end")
					if not UnInstallStack.javaPanelManager.feedBackCheck[0]:
						self.error=True
						self.totalError+=1
					self.pkgProcessed=False
							
		
		else:
			if self.totalError>0:
				self.showError=True

			self.core.mainStack.isProgressBarVisible=False
			self.core.mainStack.isProcessRunning=False
			self.core.mainStack.endProcess=True
			self.core.mainStack.feedbackCode=""
			self.core.mainStack.enableApplyBtn=True
			self.core.javaStack.enableJavaList=True
			self.core.javaStack.isAllInstalled=UnInstallStack.javaPanelManager.isAllInstalled()
			self.core.javaStack.totalErrorInProcess=UnInstallStack.javaPanelManager.totalUninstallError
			self.core.mainStack.manageRemoveBtn()
			UnInstallStack.javaPanelManager.getConfigurationOptions()
			UnInstallStack.javaPanelManager.updateJavaRegister()
			self.core.settingsStack.getInfo()
			self.uninstallProcessTimer.stop()
			
			if self.showError:
				if self.countLimit==1:
					self.core.mainStack.showStatusMessage=[True,UnInstallStack.javaPanelManager.feedBackCheck[1],UnInstallStack.javaPanelManager.feedBackCheck[2]]
				else:
					self.core.mainStack.showStatusMessage=[True,UnInstallStack.javaPanelManager.ERROR_PARTIAL_UNINSTALL,"Error"]
			else:
				self.core.mainStack.showStatusMessage=[True,UnInstallStack.javaPanelManager.feedBackCheck[1],UnInstallStack.javaPanelManager.feedBackCheck[2]]
				

		if UnInstallStack.javaPanelManager.removePkgLaunched:
			if not UnInstallStack.javaPanelManager.removePkgDone:
				if not os.path.exists(UnInstallStack.javaPanelManager.tokenUnInstall[1]):
					UnInstallStack.javaPanelManager.removePkgDone=True
		
	#def _uninstallProcessTimerRet

#class UnInstallStack

from . import Core

