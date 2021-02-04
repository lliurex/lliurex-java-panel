#!/usr/bin/env python3
import sys
import os
from PyQt5 import uic
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtCore import Qt,QEvent,QPoint,QSize
from PyQt5.QtWidgets import QLabel, QWidget, QToolButton,QVBoxLayout,QHBoxLayout,QMenu,QToolTip


from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

class ConfigurationBox(QWidget):
	def __init__(self):
		super(ConfigurationBox, self).__init__() # Call the inherited classes __init__ method
		
		self.core=Core.Core.get_core()
		ui_file=self.core.rsrc_dir+"configurationBox.ui"
		uic.loadUi(ui_file, self) # Load the .ui fil
		self.boxConfigurations=self.findChild(QVBoxLayout,'configurationBox')
		self.scrollArea=self.findChild(QWidget,'scrollAreaWidgetContents')
		self.scrollArea.setStyleSheet("background-color:white")
		self.boxConfigurations.setAlignment(Qt.AlignTop)
	
	def drawConfigurationList(self):
		
		self.jre_alternatives={}
		self.firefox_alternatives={}
		self.cpanel_alternatives={}

		self.boxDelete()
		
		self.num_separators=0
		self.count=0
		self.cpanel_alternatives=self.core.javaPanelManager.cpanel_alternatives
		self.jws_alternatives=self.core.javaPanelManager.jws_alternatives
		self.jre_alternatives=self.core.javaPanelManager.jre_alternatives
		self.firefox_alternatives=self.core.javaPanelManager.firefox_alternatives
		
		if len(self.cpanel_alternatives)>0:
			self.num_separators+=1
		if len(self.jws_alternatives)>0:
			self.num_separators+1
		if len(self.jre_alternatives)>0:
			self.num_separators+=1
		if len(self.firefox_alternatives)>0:
			self.num_separators+=1
		
		alternative_type=""

		if len(self.cpanel_alternatives)>0:
			alternative_type="cpanel"
			self.count+=1
			title=_("Java Control Panel. Select one tu run it")
			self.newConfigurationBox(self.cpanel_alternatives,'cpanel.png',title,alternative_type)	
		
		if len(self.jws_alternatives)>0:
			alternative_type="jws"
			title=_("Java Web Start. Alternative configured:")
			self.count+=1
			self.newConfigurationBox(self.jre_alternatives,'jre.png',title,alternative_type)
		
		if len(self.jre_alternatives)>0:
			alternative_type="jre"
			title=_("Java Runtime Environment. Alternative configured:")
			self.count+=1
			self.newConfigurationBox(self.jre_alternatives,'jre.png',title,alternative_type)
				
		if len(self.firefox_alternatives)>0:
			alternative_type="firefox"
			title=_("Firefox plugin. Alternative configured:")
			self.count+=1
			self.newConfigurationBox(self.firefox_alternatives,'firefox.png',title,alternative_type)
	
	#def drawConfigurationList

	def newConfigurationBox(self,info,iconName,title,alternative_type):

		hbox=QHBoxLayout()
		hbox.setContentsMargins(0,0,0,0)
		hbox.setSpacing(0)
		
		icon=QLabel()
		box_image=self.core.rsrc_dir+iconName
		#pixmap=QtGui.QPixmap(box_image).scaled(70,70)
		pixmap=QPixmap(box_image)
		icon.setPixmap(pixmap)
		icon.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		icon.setMinimumSize(90,100)
		icon.setMaximumSize(90,100)
		icon.current=False
		icon.alternative_type=alternative_type
		hbox.addWidget(icon)
		
		name=QLabel()
		name.setText(title)
		name.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

		if self.count<self.num_separators:
			name.setStyleSheet("font:10pt;border:3px solid silver;border-top:0px;border-right:0px;border-left:0px;margin-top:0px;")
		else:
			name.setStyleSheet("font:10pt")
		name.current=False
		name.alternative_type=alternative_type
		hbox.addWidget(name,-1)
		
		try:
			default=QLabel()
			for item in info:
				if info[item]["default"]:
					text=item
		except:
			text=""			
		
		default.setText(text)
		default.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		
		if self.count<self.num_separators:
			default.setStyleSheet("font:10pt;padding:15px;border:3px solid silver;border-top:0px;border-right:0px;border-left:0px;margin-top:0px;")
		else:
			default.setStyleSheet("font:10pt;padding:15px")

		default.setMinimumHeight(100)
		default.setMaximumHeight(100)
		default.current=True
		default.alternative_type=alternative_type
		hbox.addWidget(default)
		
		menu =QMenu()
		for item in info:
			action = menu.addAction(item)
			action.triggered.connect(lambda chk, item=item: self.itemClicked(item,info[item]["cmd"],alternative_type))

		pushbutton =QToolButton()
		icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"editor.svg"))
		pushbutton.setIcon(icn)
		pushbutton.setIconSize(QSize(16,16))
		pushbutton.setToolTip(_("Click to select an option"))
		pushbutton.clicked.connect(lambda:self.buttonPress(alternative_type))
		pushbutton.current=False
		pushbutton.alternative_type=alternative_type
		pushbutton.setPopupMode(QToolButton.InstantPopup)
		pushbutton.setStyleSheet("margin-right:15px;background-color:#efefef") 
		pushbutton.setMaximumSize(40,30)
		self.setStyleSheet("""QToolTip { 
                           background-color:#efefef; 
                           color: black; 
                           border: #efefef solid 1px;
                           }""")

		self.setMenu(menu,alternative_type)
		hbox.addWidget(pushbutton)
					
		self.boxConfigurations.addLayout(hbox)
	
	

	#def newConfigurationBox	
	
	
	def setMenu(self,menu,alternative_type):

		if alternative_type=='cpanel':
			self.menuCpanel=menu
			self.setContextMenuPolicy(Qt.CustomContextMenu)
		elif alternative_type=='jws':
			self.menuJws=menu	
			self.setContextMenuPolicy(Qt.CustomContextMenu)
		elif alternative_type=='jre':
			self.menuJre=menu	
			self.setContextMenuPolicy(Qt.CustomContextMenu)
		elif alternative_type=='firefox':
			self.menuFirefox=menu	
			self.setContextMenuPolicy(Qt.CustomContextMenu)
	
	#def setMenu

	def openContextMenu(self,alternative_type):
		
		if alternative_type=='cpanel':
			self.menuCpanel.exec_(self.sender().mapToGlobal(QPoint(10,23)))
		elif alternative_type=='jws':
			self.menuJws.exec_(self.sender().mapToGlobal(QPoint(10,23)))
		elif alternative_type=='jre':
			self.menuJre.exec_(self.sender().mapToGlobal(QPoint(10,23)))
		elif alternative_type=='firefox':
			self.menuFirefox.exec_(self.sender().mapToGlobal(QPoint(10,23)))

	#def openContextMenu

	def buttonPress(self,alternative_type):
		
		self.openContextMenu(alternative_type)

	#def buttonPress	

	def itemClicked(self,text,cmd,alternative_type):
		

		for item in self.boxConfigurations.children():
			if item.itemAt(2).widget().alternative_type==alternative_type:
				item.itemAt(2).widget().setText(text)	

		if alternative_type=="cpanel":
			cmd=cmd+'&'
		else:
			self.core.mainWindow.messageLabel.setText(_("Configuration changed successfully"))
		self.core.javaPanelManager.alternativeCommand(cmd)

	#def itemClicked		

	def boxDelete(self):
		for i in range(self.boxConfigurations.count()):
			layout_item = self.boxConfigurations.itemAt(i)
			if layout_item is not None:
				self.deleteItemsOfLayout(layout_item.layout())
				self.boxConfigurations.removeItem(layout_item)
	
	#def boxDelete		

	def deleteItemsOfLayout(self,layout):
		if layout is not None:
			while layout.count():
				item = layout.takeAt(0)
				widget = item.widget()
				if widget is not None:
					widget.setParent(None)
				else:
					self.deleteItemsOfLayout(item.layout())   

	#def deleteItemsOfLayout
	    
#class ConfigurationBox
from . import Core