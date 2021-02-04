#!/usr/bin/env python3
import sys
import os
from PyQt5 import uic
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtCore import Qt,QEvent
from PyQt5.QtWidgets import QLabel, QWidget,QVBoxLayout,QHBoxLayout,QCheckBox,QSizePolicy


from . import waitingSpinner

from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class InstallersBox(QWidget):
	def __init__(self):
		super(InstallersBox, self).__init__() # Call the inherited classes __init__ method
		
		self.core=Core.Core.get_core()
		ui_file=self.core.rsrc_dir+"installersBox.ui"
		uic.loadUi(ui_file, self) # Load the .ui fil
		self.boxInstallers=self.findChild(QVBoxLayout,'installersBox')
		self.boxInstallers.setAlignment(Qt.AlignTop)
		self.scrollArea=self.findChild(QWidget,'scrollAreaWidgetContents')
		self.scrollArea.setStyleSheet("background-color:white")
		self.box_selected=[]
		self.javas_selected=[]
	
	#def __init__

	def drawInstallerList(self):
		
		self.total_javas=len(self.core.javaPanelManager.java_list)
		self.count=0
		for item in self.core.javaPanelManager.java_list:
			self.count+=1
			self.newInstallerBox(self.core.javaPanelManager.java_list[item],item)
			
	#def drawInstallerList

	def newInstallerBox(self,item,order):

		hbox=QHBoxLayout()
		hbox.setContentsMargins(0,0,0,0)
		hbox.setSpacing(0)
		
		checkbox=QCheckBox()
		checkbox.setTristate(False)
		checkbox.stateChanged.connect(self.changeState)
		
		if item["installed"]:
			checkbox.setEnabled(False)
		
		checkbox.setStyleSheet("padding:10px;height: 80px")
		checkbox.item=order
		checkbox.cmd=item["cmd"]
		checkbox.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed));
		hbox.addWidget(checkbox)
		
		icon=QLabel()
		#pixmap=QtGui.QPixmap(item["banner"]).scaled(70,70)
		pixmap=QPixmap(item["banner"])
		icon.setPixmap(pixmap)
		icon.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		#icon.setStyleSheet("background-color: white") 
		icon.setMinimumSize(70,100)
		icon.setMaximumSize(70,100)
		icon.item=order
		hbox.addWidget(icon)
		
		name=QLabel()
		name.setText(item["name"])
		name.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
		if self.count<self.total_javas:
			name.setStyleSheet("font:10pt;padding:15px;border:3px solid silver;border-top:0px;border-right:0px;border-left:0px;margin-top:0px;")
		else:
			name.setStyleSheet("font:10pt;padding:15px")


		name.item=order
		hbox.addWidget(name,-1)
		
		status=QLabel()
		if item["installed"]:
			pixmap=QPixmap(self.core.rsrc_dir+"check.png")
		else:
			
			pixmap=QPixmap(self.core.rsrc_dir+"initial.png")
	
		status.setPixmap(pixmap)
		status.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
		status.setMinimumSize(35,100)
		status.setMaximumSize(35,100)
		status.item=order
		hbox.addWidget(status)

		
		waiting=waitingSpinner.waitingSpinner()
		spinner_gif=self.core.rsrc_dir+"loading.gif"
		waiting.setGif(spinner_gif,"java")
			#waiting.setStyleSheet("background-color: white") 
		waiting.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
		waiting.setMinimumSize(35,100)
		waiting.setMaximumSize(35,100)
		waiting.item=order
		waiting.hide()
		hbox.addWidget(waiting)
			#waiting.start()
					
		self.boxInstallers.addLayout(hbox)
	
	#def newInstallerBox	


	def changeState(self,state):

		if self.sender().isChecked():
			for item in self.boxInstallers.children():
				if item.itemAt(0).widget().item==self.sender().item:	
					self.box_selected.append(item)
					self.javas_selected.append(self.sender().item)
		else:
			for item in self.boxInstallers.children():
				if item.itemAt(0).widget().item==self.sender().item:
					self.box_selected.remove(item)
					self.javas_selected.remove(self.sender().item)

	#def changeState				

#class InstallersBox

from . import Core