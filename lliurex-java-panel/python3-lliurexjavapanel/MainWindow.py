#!/usr/bin/env python3
import sys
import os
from PyQt5 import uic
from PyQt5.QtGui import QIcon,QPixmap,QPainter
from PyQt5.QtCore import Qt,QEvent,QTimeLine,QThread,pyqtSignal,QSize
from PyQt5.QtWidgets import QLabel, QWidget,QVBoxLayout,QHBoxLayout,QSizePolicy,QMainWindow,QPushButton,QStackedLayout,QDesktopWidget

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
		self.messageLabel=self.findChild(QLabel,'messageLabel')
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
		self.messageLabel.hide()
		self.applyButton.hide()
		qtRectangle = self.frameGeometry()
		centerPoint = QDesktopWidget().availableGeometry().center()
		qtRectangle.moveCenter(centerPoint)
		self.move(qtRectangle.topLeft())
		centerPoint = QDesktopWidget().availableGeometry().center()
		qtRectangle.moveCenter(centerPoint)
		self.move(qtRectangle.topLeft())
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
			self.messageLabel.show()
			self.applyButton.show()
		else:
			self.messageLabel.show()
			self.loadingBox.spinner.hide()
			self.messageLabel.setText(_("No Java version(s) availables detected"))	
	
	#def _finishProcess

	def applyButtonClicked(self):
		
		self.othersBox=[]
		self.javasToInstall=self.installersBox.javas_selected
		self.boxSelected=self.installersBox.box_selected
		#self.installersBox.scrollArea.setEnabled(False)
		self.messageLabel.setText("")
		if len(self.javasToInstall)>0:
			self.applyButton.setEnabled(False)
			self.messageLabel.setText(_("Installing selected Java version(s). Wait a moment..."))

			for item in self.boxSelected:
				item.itemAt(0).widget().setEnabled(False)
				item.itemAt(3).widget().hide()
				item.itemAt(4).widget().show()
				item.itemAt(4).widget().start()

			for item in self.installersBox.boxInstallers.children():
				if item.itemAt(0).widget().isEnabled():
					item.itemAt(0).widget().setEnabled(False)	
					self.othersBox.append(item)	

			self.install=installProcess(self.javasToInstall)
			self.install.start()
			self.install.finished.connect(self._finishInstall)
		else:
			self.messageLabel.setText(_("You must select a Java version to install"))

	#def applyButtonClicked
			
	def _finishInstall(self):

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

		for item in self.othersBox:
			item.itemAt(0).widget().setEnabled(True)
		
		if error:
			self.messageLabel.setText(_("Installing process has ending with errors"))					     
		else:
			self.messageLabel.setText(_("Installing process has ending successfully"))					     

	#def _finishInstall
			
	def changePanel(self,panel):

		if panel=="C":
			self.configurationButton.hide()
			self.messageLabel.setText("")
			self.configurationBox.drawConfigurationList()
			self.fader_widget = FaderWidget(self.QtStack.currentWidget(), self.QtStack.widget(2))
			self.QtStack.setCurrentIndex(2)
			self.installersButton.show()
			self.applyButton.setEnabled(False)

		elif panel=="I":
			self.installersButton.hide()
			self.messageLabel.setText("")
			self.fader_widget = FaderWidget(self.QtStack.currentWidget(), self.QtStack.widget(2))
			self.QtStack.setCurrentIndex(1)
			self.configurationButton.show()
			self.applyButton.setEnabled(True)
			self.configurationBox.boxDelete()
	
	#def changePanel

	def helpButtonClicked(self):

		lang=os.environ["LANG"]
		run_pkexec=False
		
		if "PKEXEC_UID" in os.environ:
			run_pkexec=True
		
		if 'ca_ES' in lang:
			cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=LliureX-Java-Panel.'
		else:
			cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=LliureX-Java-Panel'

		if not run_pkexec:
			self.fcmd="su -c '%s' $USER" %cmd
		else:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.fcmd="su -c '" +cmd+ "' "+ user
			
		os.system(self.fcmd)

	#def helpButtonClicked		

'''
if __name__ == "__main__":
   
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.loadGui()
    app.exec_()      
 '''  
from . import Core