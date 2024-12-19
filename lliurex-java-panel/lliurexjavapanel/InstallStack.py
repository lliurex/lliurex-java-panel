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

class InstallStack(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		InstallStack.javaPanelManager=self.core.javaPanelManager

	#def __init__

	def checkInternetConnection(self):

		InstallStack.javaPanelManager.checkInternetConnection()
		self.checkConnectionTimer=QTimer()
		self.checkConnectionTimer.timeout.connect(self._checkConnectionTimerRet)
		self.checkConnectionTimer.start(1000)

	#def checkInternetConnection

	def _checkConnectionTimerRet(self):

		InstallStack.javaPanelManager.getResultCheckConnection()
		if InstallStack.javaPanelManager.endCheck:
			self.checkConnectionTimer.stop()
			self.core.mainStack.feedbackCode=""
			if InstallStack.javaPanelManager.retConnection[0]:
				self.core.mainStack.isProgressBarVisible=False
				self.core.mainStack.endProcess=True
				self.core.mainStack.enableApplyBtn=True
				self.core.mainStack.showStatusMessage=[True,InstallStack.javaPanelManager.retConnection[1],"Error"]
			else:
				self.installProcess()

	#def _checkConnectionTimerRet

	def installProcess(self):

		self.totalError=0
		self.core.javaStack.totalErrorInProcess=0
		self.launchedProcess="install"
		self._initInstallProcess()
		self.installProcessTimer=QTimer(None)
		self.installProcessTimer.timeout.connect(self._installProcessTimerRet)
		self.installProcessTimer.start(100)		

	#def _installProcess

	def _initInstallProcess(self):

		InstallStack.javaPanelManager.initInstallProcess()
		self.error=False
		self.showError=False
		self.endAction=False
		self.pkgProcessed=False
		countLimit=len(InstallStack.javaPanelManager.javaSelected)
		if countLimit==0:
			self.countLimit=1
		else:
			self.countLimit=countLimit

		self.pkgToSelect=-1
		self.pkgToProcess=""

	#def _initInstallProcess

	def _installProcessTimerRet(self):

		if not InstallStack.javaPanelManager.updateReposLaunched:
			self.core.mainStack.feedbackCode=InstallStack.javaPanelManager.MSG_FEEDBACK_INSTALL_REPOSITORIES
			InstallStack.javaPanelManager.updateReposLaunched=True
			self.core.mainStack.currentCommand=InstallStack.javaPanelManager.getUpdateReposCommand()
			self.core.mainStack.endCurrentCommand=True
		
		if InstallStack.javaPanelManager.updateReposDone:
			if not self.pkgProcessed:
				if not self.endAction:
					self.pkgToSelect+=1
					if self.pkgToSelect<self.countLimit:
						self.pkgToProcess=InstallStack.javaPanelManager.javaSelected[self.pkgToSelect]
						InstallStack.javaPanelManager.initPkgInstallProcess(self.pkgToProcess)
						self.core.javaStack.updateResultJavasModel('start')
					else:
						self.endAction=True

				self.pkgProcessed=True

			if not self.endAction:
				if not InstallStack.javaPanelManager.installAppLaunched:
					self.core.mainStack.feedbackCode=InstallStack.javaPanelManager.MSG_FEEDBACK_INSTALL_INSTALL
					InstallStack.javaPanelManager.installAppLaunched=True
					self.core.mainStack.currentCommand=InstallStack.javaPanelManager.getInstallCommand(self.pkgToProcess)
					self.core.mainStack.endCurrentCommand=True

				if InstallStack.javaPanelManager.installAppDone:
					if not InstallStack.javaPanelManager.checkInstallLaunched:
						InstallStack.javaPanelManager.checkInstallLaunched=True
						InstallStack.javaPanelManager.checkInstall(self.pkgToProcess)

					if InstallStack.javaPanelManager.checkInstallDone:
						self.core.javaStack.updateResultJavasModel('end')
						if InstallStack.javaPanelManager.feedBackCheck[0]:
							self.pkgProcessed=False
						else:
							self.error=True
							self.pkgProcessed=False
							self.totalError+=1
						
		if self.endAction:
			if self.totalError>0:
				self.showError=True

			self.core.mainStack.isProgressBarVisible=False
			self.core.mainStack.endProcess=True
			self.core.mainStack.feedbackCode=""
			self.core.mainStack.isProcessRunning=False
			self.core.javaStack.isAllInstalled=InstallStack.javaPanelManager.isAllInstalled()
			self.core.javaStack.totalErrorInProcess=self.totalError
			self.core.javaStack.enableJavaList=True
			self.core.mainStack.manageRemoveBtn()
			InstallStack.javaPanelManager.getConfigurationOptions()
			InstallStack.javaPanelManager.updateJavaRegister()
			self.core.settingsStack.getInfo()
			self.installProcessTimer.stop()

			if self.showError:
				if self.countLimit==1:
					self.core.mainStack.showStatusMessage=[True,InstallStack.javaPanelManager.feedBackCheck[1],InstallStack.javaPanelManager.feedBackCheck[2]]
				else:
					self.core.mainStack.showStatusMessage=[True,InstallStack.javaPanelManager.ERROR_PARTIAL_INSTALL,"Error"]
				#InstallStack.javaPanelManager.clearEnvironment()
			else:
				self.core.mainStack.enableApplyBtn=True
				self.core.javaStack.enablePkgList=True
				self.core.mainStack.showStatusMessage=[True,InstallStack.javaPanelManager.feedBackCheck[1],InstallStack.javaPanelManager.feedBackCheck[2]]
				
				#InstallStack.javaPanelManager.clearEnvironment()

		
		if InstallStack.javaPanelManager.updateReposLaunched:
			if not InstallStack.javaPanelManager.updateReposDone:
				if not os.path.exists(InstallStack.javaPanelManager.tokenUpdaterepos[1]):
					InstallStack.javaPanelManager.updateReposDone=True

		if self.pkgProcessed:
			if InstallStack.javaPanelManager.installAppLaunched:
				if not InstallStack.javaPanelManager.installAppDone:
					if not os.path.exists(InstallStack.javaPanelManager.tokenInstall[1]):
						InstallStack.javaPanelManager.installAppDone=True

	
	#def _installProcessTimerRet

#class InstallStack

from . import Core

