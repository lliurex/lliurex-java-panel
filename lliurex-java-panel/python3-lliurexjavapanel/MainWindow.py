#!/usr/bin/env python3
import sys
import os
from PyQt5 import uic
from PyQt5.QtGui import QIcon,QPixmap,QPainter
from PyQt5.QtCore import Qt,QEvent,QTimeLine,QThread,pyqtSignal,QSize,QObject
from PyQt5.QtWidgets import QLabel, QWidget,QVBoxLayout,QHBoxLayout,QSizePolicy,QMainWindow,QPushButton,QStackedLayout,QDesktopWidget,QProgressBar

import time
import subprocess
import pwd

from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class gatherInfo(QThread):
	def __init__(self,*args):
		QThread.__init__(self)

		self.errMsg=""
		self.err=0
		self.core=Core.Core.get_core()
	#def __init__
		
	def run(self,*args):

		try:
			self.core.javaPanelManager.getSupportedJava()
		except Exception as e:
			self.errMsg=("Failed when updating config: %s")%e
			self.err=1
	#def run	

#clas gatherInfo

class installProcess(QThread):

	def __init__(self,*args):
		
		QThread.__init__(self)
		self.errMsg=""
		self.err=0
		self.core=Core.Core.get_core()
		self.java_list=args[0]
	#def __init__

	def run(self,*args):

		try:
			self.core.javaPanelManager.installJava(self.java_list)
		except Exception as e:
			self.errMsg=("Failed when updating config: %s")%e
			self.err=1
	#def run
# class installProcess

class getPackages(QThread):

	def __init__(self,*args):
		
		QThread.__init__(self)
		self.core=Core.Core.get_core()
		self.java_list=args[0]

	
	#def __init__

	def run(self,*args):

		self.core.javaPanelManager.getNumberPackages(self.java_list)
	#def run

#class getPackages

class Worker(QObject):

	_finished=pyqtSignal()
	_progress=pyqtSignal(str)

	def __init__(self,*args):
		
		QObject.__init__(self)
		self.core=Core.Core.get_core()
		self.maxRetry=3
		self.timeToCheck=1
		self.isWorked=False
		self.aptStop=False
		self.aptRun=True
		self.unpackedRun=False
		self.count=0
		self.running=False
		self.countDown=self.maxRetry
	
	#def __init__

	def run(self):

		while self.running:
			self._updateProgress()
			time.sleep(self.timeToCheck)
	
	#def run

	def _updateProgress(self):

		if not self.isWorked:
			self.isWorked=True
			if not self.aptStop:
				isAptRunning=self.core.javaPanelManager.isAptRunning()
				if self.count==2:
					self.aptRun=isAptRunning
				else:
					self.count+=1

			if not self.aptRun:
				if not self.aptStop:	
					self._progress.emit("unpack")
					self.aptStop=True
					self.unpackedRun=True

				if self.countDown==self.maxRetry:
					self.countDown=0
					if self.unpackedRun:
						self.core.javaPanelManager.checkProgressUnpacked()
						if self.core.javaPanelManager.progressUnpacked!=len(self.core.javaPanelManager.initialNumberPackages):
							self._progress.emit("unpack")
						else:
							self._progress.emit("install")
							self.unpackedRun=False
					else:
						self.core.javaPanelManager.checkProgressInstallation()
						if self.core.javaPanelManager.progressInstallation!=len(self.core.javaPanelManager.initialNumberPackages):
							self._progress.emit("install")
						else:
							self.running=False
							self._progress.emit("end")
							self._finished.emit()
				else:
					self.countDown+=1

			self.isWorked=False

	#def _updateProgress

class FaderWidget(QWidget):
	
	def __init__(self, old_widget, new_widget):

		QWidget.__init__(self, new_widget)
		self.old_pixmap = QPixmap(new_widget.size())
		old_widget.render(self.old_pixmap)
		self.pixmap_opacity = 1.0
		self.timeline = QTimeLine()
		self.timeline.valueChanged.connect(self.animate)
		self.timeline.finished.connect(self.close)
		self.timeline.setDuration(222)
		self.timeline.start()
		self.resize(new_widget.size())
		self.show()
	#def __init__

	def paintEvent(self, event):

		painter = QPainter()
		painter.begin(self)
		painter.setOpacity(self.pixmap_opacity)
		painter.drawPixmap(0, 0, self.old_pixmap)
		painter.end()
	
	#def paint
	def animate(self, value):

		self.pixmap_opacity = 1.0 - value
		self.repaint()

	#def animante
#class FaderWidget	

class MainWindow(QMainWindow):
	
	def __init__(self):

		super(MainWindow, self).__init__() # Call the inherited classes __init__ method
		self.core=Core.Core.get_core()
		
	def loadGui(self):

		ui_file=self.core.rsrc_dir+"mainWindow.ui"
		uic.loadUi(ui_file, self) # Load the .ui file
		
		self.optionsBox=self.findChild(QHBoxLayout,'optionsBox')
		self.installersButton=self.findChild(QPushButton,'installersButton')
		icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"view-list-details.svg"))
		self.installersButton.setIcon(icn)
		self.installersButton.setText(_("Installers"))
		self.installersButton.clicked.connect(lambda:self.changePanel("I"))
		self.configurationButton=self.findChild(QPushButton,"configurationButton")
		icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"configure.svg"))
		self.configurationButton.setIcon(icn)
		#self.configurationButton.setIconSize(QSize(16,16))
		self.configurationButton.setText(_("Configuration Options"))
		self.configurationButton.clicked.connect(lambda:self.changePanel("C"))
		self.mainBox=self.findChild(QVBoxLayout,'mainBox')
		self.bannerBox=self.findChild(QLabel,'bannerLabel')
		self.bannerBox.setStyleSheet("background-color: #7f0907") 
		self.messageBox=self.findChild(QVBoxLayout,'messageBox')
		self.messageImg=self.findChild(QLabel,'messageImg')
		self.messageLabel=self.findChild(QLabel,'messageLabel')
		self.progressBar=self.findChild(QProgressBar,'progressBar')
		self.controlsBox=self.findChild(QVBoxLayout,'controlsBox')
		self.applyButton=self.findChild(QPushButton,'applyButton')
		icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"gtk-ok.svg"))
		self.applyButton.setIcon(icn)
		self.applyButton.setText(_("Install"))
		self.applyButton.clicked.connect(self.applyButtonClicked)
		self.helpButton=self.findChild(QPushButton,'helpButton')
		icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"help-whatsthis.svg"))
		self.helpButton.setIcon(icn)
		self.helpButton.setText(_("Help"))
		self.helpButton.clicked.connect(self.helpButtonClicked)
		
		self.loadingBox=self.core.loadingBox
		self.installersBox=self.core.installersBox
		self.configurationBox=self.core.configurationBox

		self.QtStack=QStackedLayout()
		self.QtStack.addWidget(self.loadingBox)
		self.QtStack.addWidget(self.installersBox)
		self.QtStack.addWidget(self.configurationBox)
		
		self.mainBox.addLayout(self.QtStack)
		self.gatherInfo=gatherInfo()
		self.installersButton.hide()
		self.configurationButton.hide()
		#self.messageLabel.hide()
		self._manageMsgBox(True,False)	
		self.applyButton.hide()
		self.helpButton.hide()

		qtRectangle = self.frameGeometry()
		centerPoint = QDesktopWidget().availableGeometry().center()
		qtRectangle.moveCenter(centerPoint)
		self.move(qtRectangle.topLeft())
		centerPoint = QDesktopWidget().availableGeometry().center()
		qtRectangle.moveCenter(centerPoint)
		self.move(qtRectangle.topLeft())
		self.exitLocked=True
		self.gatherInfo.start()
		self.gatherInfo.finished.connect(self._finishProcess)
		
	#def loadGui


	def _finishProcess(self):

		self.loadingBox.spinner.stop()
		if len(self.core.javaPanelManager.java_list)>0:
			self.installersBox.drawInstallerList()
			self.fader_widget = FaderWidget(self.QtStack.currentWidget(), self.QtStack.widget(1))
			self.QtStack.setCurrentIndex(1)
			self.configurationButton.show()
			self._manageMsgBox(True,False)	
			#self.messageLabel.show()
			self.applyButton.show()
			self.helpButton.show()
		else:
			#self.messageLabel.show()
			self._manageMsgBox(False,True)	
			self.loadingBox.spinner.hide()
			self.messageLabel.setText(_("No Java version(s) availables detected"))	

		self.exitLocked=False

	#def _finishProcess

	def applyButtonClicked(self):
		
		self.othersBox=[]
		self.javasToInstall=self.installersBox.javas_selected
		self.boxSelected=self.installersBox.box_selected
		#self.installersBox.scrollArea.setEnabled(False)
		self._manageMsgBox(True,False)	
		
		self.messageLabel.setText("")
		if len(self.javasToInstall)>0:
			self.applyButton.setEnabled(False)
			self.configurationButton.setEnabled(False)
			self.helpButton.setEnabled(False)
			#self.messageLabel.setText(_("Installing selected Java version(s). Wait a moment..."))

			for item in self.boxSelected:
				item.itemAt(0).widget().setEnabled(False)
				item.itemAt(3).widget().hide()
				item.itemAt(4).widget().show()
				item.itemAt(4).widget().start()

			for item in self.installersBox.boxInstallers.children():
				if item.itemAt(0).widget().isEnabled():
					item.itemAt(0).widget().setEnabled(False)	
					self.othersBox.append(item)

			self.exitLocked=True
			'''
			self.install=installProcess(self.javasToInstall)
			self.install.start()
			self.install.finished.connect(self._finishInstall)
			'''
			self.getPackages=getPackages(self.javasToInstall)
			self._manageMsgBox(True,False)
			self.messageLabel.setText(_("1 of 5: Obtaining information about Java(s) to install..."))
			self.progressBar.show()
			self.getPackages.start()
			self.getPackages.finished.connect(self._finishGetPackages)

		else:
			self._manageMsgBox(False,True)	
			self.messageLabel.setText(_("You must select a Java version to install"))

	#def applyButtonClicked

	def _finishGetPackages(self):

		self.messageLabel.setText(_("2 of 5: Downloading packages..."))
		self.progressBar.setValue(100)
		
		self.checkProgress=QThread()
		self.worker=Worker()
		self.worker.moveToThread(self.checkProgress)
		self.checkProgress.started.connect(self.worker.run)
		self.worker._finished.connect(self.checkProgress.quit)
		self.worker._progress.connect(self._updateMessage)
		self.install=installProcess(self.javasToInstall)
		self.install.start()
		self.install.finished.connect(self._finishInstall)
		self.worker.running=True
		self.checkProgress.start()

	#def _finishGetPackages
	
	def _updateMessage(self,step):

		if step=="unpack":
			self.messageLabel.setText(_("3 of 5: Unpacking packages: %s of %s packages")%(str(self.core.javaPanelManager.progressUnpacked),len(self.core.javaPanelManager.initialNumberPackages)))
		elif step=="install":
			self.messageLabel.setText(_("4 of 5: Configuring packages: %s of %s packages")%(str(self.core.javaPanelManager.progressInstallation),len(self.core.javaPanelManager.initialNumberPackages)))
		elif step=="end":
			self.messageLabel.setText(_("5 of 5: Finishing the installation..."))
		
		self._updateProgressBar(step)
	#def _updateMessage		

	def _updateProgressBar(self,step):

		if step=="unpack":
			if self.core.javaPanelManager.progressUnpackedPercentage==0.00:
				self.progressBar.setValue(200)
			else:
				p_value=2+float(self.core.javaPanelManager.progressUnpackedPercentage)
				self.progressBar.setValue(p_value*100)
		elif step=="install":
			if self.core.javaPanelManager.progressInstallationPercentage==0.00:
				self.progressBar.setValue(300)
			else:
				p_value=3+float(self.core.javaPanelManager.progressInstallationPercentage)
				self.progressBar.setValue(p_value*100)
		elif step=="end":
			self.progressBar.setValue(400)

	#def _updateProgressBar

			
	def _finishInstall(self):

		self.progressBar.hide()
		self.worker.running=False

		result=self.core.javaPanelManager.result_install
		error=False
		for item in result:
			if result[item]:
				for element in self.boxSelected:
					if element.itemAt(4).widget().item==item:
						element.itemAt(4).widget().stop()
						element.itemAt(4).widget().hide()
						pixmap=QPixmap(self.core.rsrc_dir+"check.png")
						element.itemAt(3).widget().setPixmap(pixmap)
						element.itemAt(0).widget().setChecked(False)
						element.itemAt(3).widget().show()
			else:
				for element in self.boxSelected:
					if element.itemAt(4).widget().item==item:
						element.itemAt(4).widget().stop()
						element.itemAt(4).widget().hide()
						pixmap=QPixmap(self.core.rsrc_dir+"error.png")
						element.itemAt(3).widget().setPixmap(pixmap)
						element.itemAt(0).widget().setChecked(False)
						element.itemAt(0).widget().setEnabled(True)
						element.itemAt(3).widget().show()
				error=True		
		
		self.applyButton.setEnabled(True)
		self.configurationButton.setEnabled(True)
		self.helpButton.setEnabled(True)

		for item in self.othersBox:
			item.itemAt(0).widget().setEnabled(True)
		
		if error:
			self._manageMsgBox(False,True)	
			self.messageLabel.setText(_("Installing process has ending with errors"))					     
		else:
			self._manageMsgBox(False,False)	
			self.messageLabel.setText(_("Installing process has ending successfully"))					     

		self.exitLocked=False

	#def _finishInstall
			
	def changePanel(self,panel):

		if panel=="C":
			self.configurationButton.hide()
			self.progressBar.hide()
			self._manageMsgBox(True,False)	
			self.messageLabel.setText("")
			self.configurationBox.drawConfigurationList()
			self.fader_widget = FaderWidget(self.QtStack.currentWidget(), self.QtStack.widget(2))
			self.QtStack.setCurrentIndex(2)
			self.installersButton.show()
			self.applyButton.setEnabled(False)

		elif panel=="I":
			self.installersButton.hide()
			self._manageMsgBox(True,False)	
			self.messageLabel.setText("")
			self.fader_widget = FaderWidget(self.QtStack.currentWidget(), self.QtStack.widget(2))
			self.QtStack.setCurrentIndex(1)
			self.configurationButton.show()
			self.applyButton.setEnabled(True)
			self.configurationBox.boxDelete()
	
	#def changePanel

	def helpButtonClicked(self):

		lang=os.environ["LANG"]
		language=os.environ["LANGUAGE"]
		run_pkexec=False
		
		if "PKEXEC_UID" in os.environ:
			run_pkexec=True

		exec_lang=""
		app_lang=""

		if language=="":
			app_lang=lang
		else:
			language=language.split(":")[0]
			app_lang=language
		
		if 'valencia' in app_lang:
			exec_lang="LANG=ca_ES.UTF-8@valencia"
			cmd=exec_lang+' xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=LliureX+Java+Panel.'
		else:
			exec_lang="LANG=es_ES.UTF-8"
			cmd=exec_lang+' xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=LliureX-Java-Panel'

		if not run_pkexec:
			self.fcmd="su -c '%s &' $USER" %cmd
		else:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.fcmd="su -c '" +cmd+ " &' "+ user
			
		os.system(self.fcmd)

	#def helpButtonClicked		

	def closeEvent(self,event):

		if self.exitLocked:
			event.ignore()
		else:
			event.accept()			

	#def closeEvent

	def _manageMsgBox(self,hide,error):

		self.progressBar.hide()
		if hide:
			self.messageImg.setStyleSheet("background-color: transparent")
			self.messageLabel.setStyleSheet("background-color: transparent")
			self.messageImg.hide()
			self.messageLabel.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)

		else:
			if error:
				self.messageImg.setStyleSheet("border-bottom: 1px solid #da4453;border-left: 1px solid #da4453;border-top: 1px solid #da4453;background-color: #ebced2")
				self.messageLabel.setStyleSheet("border-bottom: 1px solid #da4453;border-right: 1px solid #da4453;border-top: 1px solid #da4453;background-color: #ebced2")
				pixmap=QPixmap(self.core.rsrc_dir+"dialog-error.png")
				self.messageImg.setPixmap(pixmap)
				self.messageImg.show()
				self.messageLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
				self.messageLabel.show()			
			else:
				self.messageImg.setStyleSheet("border-bottom: 1px solid #27ae60;border-left: 1px solid #27ae60;border-top: 1px solid #27ae60;background-color: #c7e3d4")
				self.messageLabel.setStyleSheet("border-bottom: 1px solid #27ae60;border-right: 1px solid #27ae60;border-top: 1px solid #27ae60;background-color: #c7e3d4")
				pixmap=QPixmap(self.core.rsrc_dir+"dialog-positive.png")
				self.messageImg.setPixmap(pixmap)
				self.messageImg.show()
				self.messageLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
				self.messageLabel.show()			

	#def _manageMsgBox
	
from . import Core
