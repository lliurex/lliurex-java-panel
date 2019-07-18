#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')

import cairo
import os
import threading
import ConfigParser
import platform
import subprocess
import sys
import shutil
from math import pi

from gi.repository import Gtk, Gdk, GObject, GLib, PangoCairo, Pango

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


import gettext
gettext.textdomain('lliurex-java-panel')
_ = gettext.gettext


BASE_DIR="/usr/share/lliurex-java-panel/"
RSRC_DIR=BASE_DIR+"rsrc/"
SHADOW_BANNER=RSRC_DIR+"shadow.png"
UNKNOWN_BANNER=RSRC_DIR+"unknown.png"
BANNERS_PATH=BASE_DIR+"banners/"
JAVAS_CONFIG_PATH=BASE_DIR+"supported-javas/"
SWING_FILE=BASE_DIR+"swing.properties"
PACKAGE_NAME="lliurex-java-panel"


CURRENT_PLATFORM=platform.machine()

class GridButton:
	
	def __init__(self,info):
		
		self.info=info
		self.info["installed"]=False
		self.info["shadow_alpha"]=0.1
		self.info["animation_active"]=False
		self.info["shadow_start"]=0
		self.info["available"]=True
		
		if os.path.exists(BANNERS_PATH+self.info["pkg"]+".png"):
			self.info["image"]=BANNERS_PATH+self.info["pkg"]+".png"
		else:
			self.info["image"]=UNKNOWN_BANNER
		
	#def init
	
	
#class GridButton


class ConfButton:
	
	def __init__(self,info):
		
		self.txt=info["txt"]
		self.icon=info["icon"]
		self.name=info["name"]
		self.da=None
		if "active" not in info:
			self.active=False
		else:
			self.active=info["active"]
		
	#def

#class ConfButton
	
	
class Alternative(Gtk.RadioButton):

	def __init__(self,label,command):
		
		Gtk.RadioButton.__init__(self, label)
		self.command=command
		#self.connect("toggled",self.alternative_toggled)
		
	def alternative_toggled(self,widget):
		
		if widget.get_active():
			print("* Executing %s ..."%self.command)
			os.system(self.command)
		
#class Alternative


class CpanelButton(Gtk.Button):

	def __init__(self,label,command):
		
		Gtk.Button.__init__(self, label)
		self.command=command+"&"
		self.connect("clicked",self.button_clicked)
		
	
	def button_clicked(self,widget):
		
		print("* Executing %s ..."%self.command)
		os.system(self.command)
		
#class CpanelButton



class ConfigurationParser:
	
	def __init__(self):
		pass
	
	def load_plugin(self,path):
	
		try:
			config = ConfigParser.ConfigParser()
			config.optionxform=str
			config.read(path)
			if config.has_section("JAVA"):
				info={}
				info["pkg"]=config.get("JAVA","pkg")
				info["name"]=config.get("JAVA","name")
				info["cmd"]=config.get("JAVA","cmd")
				try:
					info["swing"]=config.get("JAVA","swing")
				except Exception as e:
					pass	
				return GridButton(info)
				
		except Exception as e:
			print e
			return None
	
	
#class ConfigParser


class CustomColor:
	
	def __init__(self,r,g,b):
		
		self.r=r/255.0
		self.g=g/255.0
		self.b=b/255.0

#class CustomColor		

class AwesomeTabs:
	
	def __init__(self):
		
		self.configuration_parser=ConfigurationParser()
		
		self.current_tab=-1
		self.current_width=0
		self.animation_left=False
		self.animation_right=False
		
		self.current_red_width=0
		self.current_red_pos=0
		self.configuration_start=0
		
		self.first_run=True
		self.update_alternatives=False
		
		self.current_grid_width=0
		self.current_grid_height=0
		
		self.max_grid_width=2
		
		self.dark_gray=CustomColor(130.0,151.0,161.0)
		self.light_gray=CustomColor(185.0,195.0,195.0)
		
		self.green=CustomColor(74.0,166.,69.0)
		self.light_green=CustomColor(88.0,208.0,86.0)
		
		
		self.conf_light=CustomColor(49.0,55.0,66.0)
		self.conf_dark=CustomColor(30.0,36.0,42.0)
		
		self.conf_light_shadow=CustomColor(107.0,116.0,137.0)
		self.conf_dark_shadow=CustomColor(0,0,0)
		
		self.current_conf_height=0
		self.conf_buttons=[]
		self.start_gui()
		
		
	#def __init__
	
	
	
	def start_gui(self):
		
		builder=Gtk.Builder()
		builder.set_translation_domain('lliurex-java-panel')
		glade_path=RSRC_DIR+"lliurex-java-panel.ui"
		builder.add_from_file(glade_path)
		
		self.installers_eb=builder.get_object("installers_eventbox")
		self.installers_eb.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
		self.installers_eb.connect("button-press-event",self.label_clicked,0)
		
		self.configuration_eb=builder.get_object("configuration_eventbox")
		self.configuration_eb.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
		self.configuration_eb.connect("button-press-event",self.label_clicked,1)
		
		self.installers_label=builder.get_object("installers_label")
		self.configuration_label=builder.get_object("configuration_label")
		self.alternatives_label=builder.get_object("alternatives_label")
		
		self.top_divider_da=builder.get_object("top_divider_drawingarea")
		self.bottom_divider_da=builder.get_object("bottom_divider_drawingarea")
		#self.install_da.connect("draw",self.drawing_label_event,0)
		self.top_divider_da.connect("draw",self.draw_top_divider)
		self.bottom_divider_da.connect("draw",self.draw_bottom_divider)
		
		self.button_scroll=builder.get_object("button_scrolledwindow")
		self.main_box=builder.get_object("main_box")
		'''
		self.close_eb=builder.get_object("close_eventbox")
		self.close_da=builder.get_object("close_drawingarea")
		self.close_eb.connect("button-press-event",self.quit)
		self.close_da.connect("draw",self.draw_close_button)
		'''
		self.close_button=builder.get_object("close_button")
		self.close_button.connect("clicked",self.quit)
		
		
		self.stack = Gtk.Stack()
		self.stack.set_transition_duration(1000)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		
		self.installers_grid=builder.get_object("button_grid")
		self.configuration_box=builder.get_object("configuration_box")
		
		'''
		grid=GridButton("oracle-java6","Oracle Java 6")
		self.add_grid_button(grid)
		
		grid=GridButton("oracle-java7","Oracle Java 7")
		self.add_grid_button(grid)
		
		grid=GridButton("oracle-java8","Oracle Java 8")
		self.add_grid_button(grid)
		
		grid=GridButton("openjdk6","Open JRE 6")
		self.add_grid_button(grid)
		
		grid=GridButton("openjdk7","Open JRE 7")
		self.add_grid_button(grid)
		'''
		
			
		
		
		self.stack.add_titled(self.button_scroll, "installers", "Installers")
		self.stack.add_titled(self.configuration_box, "configuration", "Configuration")
		
		self.main_box.add(self.stack)
		
		self.main_window=builder.get_object("main_window")
		
		
		self.main_window.connect("destroy",self.quit)
		
		
		self.progress_window=builder.get_object("progress_window")
		self.pbar=builder.get_object("progressbar")
		self.progress_window.set_transient_for(self.main_window)
		
		self.gather_window=builder.get_object("gather_window")
		self.gather_pbar=builder.get_object("progressbar1")
		self.progress_label=builder.get_object("progress_label")
		
		self.label_clicked(None,None,0)
		
		self.confbutton_grid=builder.get_object("confbutton_grid")
		
		info={}
		info["txt"]="Control Panel"
		info["icon"]=RSRC_DIR+"control_panel.png"
		info["name"]="cpanel"
		info["active"]=True
		
		self.add_conf_button(info)
		
		info["txt"]="Java Web Start"
		info["icon"]=RSRC_DIR+"java_conf.png"
		info["name"]="jws"
		info["active"]=False
		
		self.add_conf_button(info)
		
		info["txt"]="Java Runtime\nEnvironment"
		info["icon"]=RSRC_DIR+"java_conf.png"
		info["name"]="jre"
		
		self.add_conf_button(info)
		
		info["txt"]="Firefox Plugin"
		info["icon"]=RSRC_DIR+"firefox.png"
		info["name"]="firefox"
		
		self.add_conf_button(info)
		
		self.configuration_box=builder.get_object("configuration_box")
		self.alternatives_box=builder.get_object("alternatives_box")
		
		self.conf_stack=Gtk.Stack()
		self.conf_stack.set_transition_duration(500)
		self.conf_stack.set_transition_type(Gtk.StackTransitionType.UNDER_DOWN)
		
		self.alternatives_box.pack_start(self.conf_stack,True,True,0)
		
		self.build_cpanel_alternatives()
		self.build_jws_alternatives()
		self.build_jre_alternatives()
		self.build_firefox_alternatives()
		self.configuration_box.show_all()

		self.set_css_info()
		
		#self.main_window.show_all()
		self.gather_window.show_all()
		GLib.timeout_add(100,self.pulsate_gathering_info)
		
		self.t=threading.Thread(target=self.gather_info)
		self.t.daemon=True
		self.t.start()
		
		
		GObject.threads_init()		
		Gtk.main()
		
	#def start_gui
	
	def gather_info(self):
		
		import time
		#base_apt_cmd="apt-cache policy "
		
		#gbs=[]
		
		for item in sorted(os.listdir(JAVAS_CONFIG_PATH)):
			if os.path.isfile(JAVAS_CONFIG_PATH+item):
				gb=self.configuration_parser.load_plugin(JAVAS_CONFIG_PATH+item)
				if gb!=None:
					sys.stdout.write("* Checking %s ...\t"%gb.info["pkg"])
					gb.info["installed"]=self.is_installed(gb.info["pkg"])
					sys.stdout.write("%s\n"%gb.info["installed"])
					#base_apt_cmd+= "%s "%gb.info["pkg"]
					base_apt_cmd = "apt-cache policy %s "%gb.info["pkg"]
					#gbs.append(gb)
					p=subprocess.Popen([base_apt_cmd],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
					output=p.communicate()
					
					if gb.info["pkg"] not in output[0]:
						available=False
					else:	
						version=output[0].split("\n")[4]
						if version !='':
							available=True
						else:
							available=False
						
					if available:
						self.add_grid_button(gb)
					else:		
						print(" [!] %s not available [!] "%gb.info["pkg"])
						gb.info["available"]=False
		
		'''			
		p=subprocess.Popen([base_apt_cmd],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
		output=p.communicate()
		
		for gb in gbs:
			
			if gb.info["pkg"] not in output[0]:
				print(" [!] %s not available [!] "%gb.info["pkg"])
				gb.info["available"]=False
				available=False
			else:
				self.add_grid_button(gb)

		'''		
	
	#def gather_info
	
	def pulsate_gathering_info(self):
		
		self.gather_pbar.pulse()
		
		if not self.t.is_alive():
			
			self.gather_window.hide()
			self.main_window.show_all()
		
		return self.t.is_alive()
		
	#def pulsate_gathering
	
	def set_css_info(self):
		
		css = """
		
		#BLUE {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#0f72ff),  to (#0f72ff));;
		
		}
		
		#BLACK{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#000000),  to (#000000));;
		
		}
		
		
		#BACK_GRADIENT{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#ffffff), to (#eceff3));;
		}
		
		#WHITE {
			color: white;
			text-shadow: 0px 1px black;
		}
		
		#MAIN_LABEL_ENABLED{
			color: #8297a1;
			font: 18pt Quattrocento Sans Bold;
		}
		
		#ALTERNATIVES_LABEL{
			color: #8297a1;
			font: 12pt Quattrocento Sans Bold;
		}
		
		#MAIN_LABEL_DISABLED{
			color: #c9d4e2;
			font: 18pt Quattrocento Sans Bold;
		}
		
		#RED_PROGRESS{
			
		/*	background-color: #FF0000;*/
			border: 0px;

		}

		.progressbar {
		/*	background-color: #ff0000;*/
		}

		GtkProgressBar.trough, .level-bar.trough {
			border: none;
			border-radius: 3px;
			/*background-color: #cfd6e6; */
		}

		#DARK_BACK{
			background-color: #070809;
		}
		
		#GREEN {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#41ff70),  to (#41ff70));;
		
		}
		
		#ORANGE {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#ff7f2a),  to (#ff7f2a));;
		
		}
		
		#LIGHTBLUE {
			-unico-border-gradient: -gtk-gradient (linear, left top, left bottom,
			from (shade (#ff0000, 0.68)),
			to (shade (#ff0000, 0.68)));
		
		}
		


		.radio#RED {
		  -gtk-icon-source: -gtk-scaled(url("/usr/share/lliurex-java-panel/rsrc/radio-unchecked.png"), url("/usr/share/lliurex-java-panel/rsrc/radio-unchecked.png")); }

		
		
		.radio:checked#RED {
		  -gtk-icon-source: -gtk-scaled(url("/usr/share/lliurex-java-panel/rsrc/radio-checked.png"), url("/usr/share/lliurex-java-panel/rsrc/radio-checked.png")); }

		GtkButton#RED GtkLabel {
			color: #8297a1;
			font: 11pt Quattrocento Sans;
		}


		"""
		self.style_provider=Gtk.CssProvider()
		self.style_provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		
		self.main_window.set_name("BACK_GRADIENT")
		self.installers_label.set_name("MAIN_LABEL_ENABLED")
		self.alternatives_label.set_name("ALTERNATIVES_LABEL")
		self.configuration_label.set_name("MAIN_LABEL_DISABLED")
		#self.pbar.set_name("RED_PROGRESS")
		self.gather_pbar.set_name("RED_PROGRESS")
		self.confbutton_grid.set_name("DARK_BACK")
		self.progress_label.set_name("ALTERNATIVES_LABEL")
		
		
	#def css_info

	
	def is_installed(self,pkg):
		
		
		p=subprocess.Popen(["dpkg-query -W -f='${db:Status-Status}' %s"%pkg],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output=p.communicate()
		
		if output[0]=="installed":
			return True
			
		return False
		
		
	#def is_installed
	
	def quit(self,widget,event=None):
		
		Gtk.main_quit()
		
	#def quit
	
	def execute(self,command):
		
		self.thread_ret=-1
		
		self.thread_ret=os.system(command)
		
	#def execute
	
	
	def pulsate_pbar(self,grid_button,da):
		
		if self.t.is_alive():
			
			self.pbar.pulse()
			
			
		if not self.t.is_alive():
			self.progress_window.hide()
			if self.thread_ret==0:
				grid_button.info["installed"]=True
				self.update_alternatives=True
				try:
					self.copy_swing_file(grid_button.info["swing"])
				except Exception as e:
					print(str(e))
					pass	
			da.queue_draw()
			
		return self.t.is_alive()
	
	#def pulsate_pbar

	def copy_swing_file(self,destPath):

		destPath_swing=destPath+"swing.properties"
		destPath_diverted=destPath_swing+".diverted"

		if not os.path.exists(destPath_swing):
			shutil.copy2(SWING_FILE,destPath)
		else:
			if not os.path.exists(destPath_diverted):
				cmd_diversion="dpkg-divert --package "+PACKAGE_NAME+" --add --rename --divert " +destPath_diverted + " "+ destPath_swing
				result=(subprocess.check_output(cmd_diversion,shell=True)).split("\n")
				if result[0]!="":
					os.symlink(SWING_FILE,destPath_swing)
				else:
					print("Unable to create diversion")


	def add_conf_button(self,info):
		
		cb=ConfButton(info)
		da=Gtk.DrawingArea()
		da.set_size_request(110,123)
		da.connect("draw",self.draw_configure_button,cb)
		da.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
		da.connect("button-press-event",self.conf_clicked,cb)
		da.show()
		self.confbutton_grid.attach(da,0,self.current_conf_height,1,1)
		self.current_conf_height+=1
		self.conf_buttons.append(cb)
		cb.da=da
		
		
	#deff add_conf_button
	

	def build_cpanel_alternatives(self):
		
		tmp_box=Gtk.VBox()
		
		alternative_list=[]
		cpanel_label_list=[]
		cpanel_cmd_list=[]
		
		# build alternatives list here
		
		# ############### #
		try:		
			java_cmd='update-alternatives --list java | grep -v "gij"'
			java_cmd_list=(subprocess.check_output(java_cmd, shell=True)).split("\n")
			java_label='update-alternatives --list java | grep -v "gij" | cut -d"/" -f5'
			java_label_list=(subprocess.check_output(java_label, shell=True)).split("\n")
			
			i=0
			for item in java_label_list:
			
				if java_label_list[i]!='':
					if not ('openjdk' in java_label_list[i]):
						cpanel_label_list.append(item)
						#cpanel_cmd_list.append(java_cmd_list[i].replace("bin/java", "bin/ControlPanel"))
						cpanel_cmd_list.append(java_cmd_list[i].replace("bin/java", "bin/jcontrol"))

					i+=1
				
			if len(cpanel_label_list)>0:	
				for x in cpanel_label_list:
					j=cpanel_label_list.index(x)
					a=CpanelButton(x.upper(),cpanel_cmd_list[j])
					#a.set_name("RED")
					#alternative_list.append(a)
					tmp_box.pack_start(a,False,False,15)
		except Exception as e:
			print e
		'''	
		if len(alternative_list) > 0:
			for alternative in alternative_list[1:]:
				alternative.join_group(alternative_list[0])
				
		
		
		for alternative in alternative_list:
			alternative.connect("toggled",alternative.alternative_toggled)
		'''
				
		self.conf_stack.add_titled(tmp_box, "cpanel", "Control Panel")

		
	#def build_cpanel_alternatives  
	
	
	def build_jws_alternatives(self):
	
		tmp_box=Gtk.VBox()
		
		alternative_list=[]
		jws_label_list=[]
		jws_cmd_list=[]
		
		# build alternatives list here
		
		# ############### #
		try:
			java_cmd='update-alternatives --list javaws | grep -v "gij"'
			java_cmd_list=(subprocess.check_output(java_cmd, shell=True)).split("\n")
			java_label='update-alternatives --list javaws | grep -v "gij" | cut -d"/" -f6'
			java_label_list=(subprocess.check_output(java_label, shell=True)).split("\n")
			i=0
			for item in java_label_list:
				if java_label_list[i]!='':
					jws_label_list.append(item)
					jws_cmd_list.append('update-alternatives --set javaws ' + java_cmd_list[i])
					i+=1
		
			if len(jws_label_list)>0:
				for x in jws_label_list:
					j=jws_label_list.index(x)
					a=Alternative(x.upper(),jws_cmd_list[j])
					a.set_name("RED")
					alternative_list.append(a)
					tmp_box.pack_start(a,False,False,15)
			
			if len(alternative_list) > 0:
				for alternative in alternative_list[1:]:
					alternative.join_group(alternative_list[0])
		except Exception as e:
			print e		
								
		# get jws configured actually
		
		# ################ #
		try:
			jws_configured_cmd='update-alternatives --get-selections |grep javaws$' 
			jws_configured_label= (subprocess.check_output(jws_configured_cmd, shell=True)).split("/")[4]	
			k=jws_label_list.index(jws_configured_label)
			alternative_list[k].set_active(True)
		except Exception as e:
			print e
			try:
				jws_remove=(subprocess.check_output(jws_configured_cmd, shell=True)).split()[2]
				remove_alternative='update-alternatives --remove "javaws"' + ' "'+ jws_remove+'"'
				os.system(remove_alternative)
				jws_configured_cmd='update-alternatives --get-selections |grep javaws$' 
				jws_configured_label= (subprocess.check_output(jws_configured_cmd, shell=True)).split("/")[4]
				k=jws_label_list.index(jws_configured_label)
				alternative_list[k].set_active(True)
			except Exception as e:
				print e
			
			
		for alternative in alternative_list:
			alternative.connect("toggled",alternative.alternative_toggled)
		
		self.conf_stack.add_titled(tmp_box, "jws", "Java Web Start")

		
	#def  build_jws_alternatives
	
	
	def build_jre_alternatives(self):
	
		tmp_box=Gtk.VBox()
		
		alternative_list=[]
		jre_label_list=[]
		jre_cmd_list=[]

		# build alternatives list here
		
		# ############### #
		try:	
			java_cmd='update-alternatives --list java | grep -v "gij"'
			java_cmd_list=(subprocess.check_output(java_cmd, shell=True)).split("\n")
			java_label='update-alternatives --list java | grep -v "gij" | cut -d"/" -f5'
			java_label_list=(subprocess.check_output(java_label, shell=True)).split("\n")
		
			i=0
			for item in java_label_list:
				if java_label_list[i]!='':
					jre_label_list.append(item)
					jre_cmd_list.append('update-alternatives --set java ' + java_cmd_list[i])
					i+=1
				
			if len(java_label_list)>0:
				for x in jre_label_list:
					j=jre_label_list.index(x)
					a=Alternative(x.upper(),jre_cmd_list[j])
					a.set_name("RED")
					alternative_list.append(a)
					tmp_box.pack_start(a,False,False,15)
			
			if len(alternative_list) > 0:
				for alternative in alternative_list[1:]:
					alternative.join_group(alternative_list[0])
		except Exception as e:
			print e
		# get jre configured actually
		
		# ################ #
		try:
			jre_configured_cmd='update-alternatives --get-selections |grep java$' 
			jre_configured_label= (subprocess.check_output(jre_configured_cmd, shell=True)).split("/")[4]	
			k=jre_label_list.index(jre_configured_label)
			alternative_list[k].set_active(True)
		except Exception as e:
			print e
		
		for alternative in alternative_list:
			alternative.connect("toggled",alternative.alternative_toggled)
		
		
		self.conf_stack.add_titled(tmp_box, "jre", "JRE Selector")

		
	#def build_jre_alternatives

	
	def build_firefox_alternatives(self):
	
		tmp_box=Gtk.VBox()
		
		alternative_list=[]
		firefox_label_list=[]
		firefox_cmd_list=[]	
		
		# build alternatives list here
		
		# ############### #
		try:
			javaplugin_cmd='update-alternatives --list mozilla-javaplugin.so | grep -v "gij"' 
			javaplugin_cmd_list=(subprocess.check_output(javaplugin_cmd, shell=True)).split("\n")
			javaplugin_label='update-alternatives --list mozilla-javaplugin.so | grep -v "gij" | cut -d"/" -f5'
			javaplugin_label_list=(subprocess.check_output(javaplugin_label, shell=True)).split("\n")
			i=0
			for item in javaplugin_label_list:
				if javaplugin_label_list[i]!='':
					firefox_label_list.append(item)
					firefox_cmd_list.append('update-alternatives --set mozilla-javaplugin.so ' + javaplugin_cmd_list[i])
					i+=1
		
			if len(firefox_label_list)>0:
				for x in firefox_label_list:
					j=firefox_label_list.index(x)
					a=Alternative(x.upper(),firefox_cmd_list[j])
					a.set_name("RED")
					alternative_list.append(a)
					tmp_box.pack_start(a,False,False,15)
			
			if len(alternative_list) > 0:
				for alternative in alternative_list[1:]:
					alternative.join_group(alternative_list[0])
		except Exception as e:
			print e		
				
					
		# get mozilla plugin configured actually
		
		# ################ #
		try:
			firefox_configured_cmd='update-alternatives --get-selections |grep mozilla-javaplugin.so' 
			firefox_configured_label= (subprocess.check_output(firefox_configured_cmd, shell=True)).split("/")[4]	
		
			k=firefox_label_list.index(firefox_configured_label)
			alternative_list[k].set_active(True)
		except Exception as e:
			print e	
		
		for alternative in alternative_list:
			alternative.connect("toggled",alternative.alternative_toggled)
		
		self.conf_stack.add_titled(tmp_box, "firefox", "Firefox Alternatives")

		
	#def  build_firefox_alternatives
	
	def refresh_alternatives(self):
		
		cpanel_alter=self.conf_stack.get_child_by_name("cpanel")
		self.conf_stack.remove(cpanel_alter)
		jws_alter=self.conf_stack.get_child_by_name("jws")
		self.conf_stack.remove(jws_alter)
		jre_alter=self.conf_stack.get_child_by_name("jre")
		self.conf_stack.remove(jre_alter)
		firefox_alter=self.conf_stack.get_child_by_name("firefox")
		self.conf_stack.remove(firefox_alter)
		self.build_cpanel_alternatives()
		self.build_jws_alternatives()
		self.build_jre_alternatives()
		self.build_firefox_alternatives()
		self.configuration_box.show_all()
		
		try:
			self.conf_stack.set_visible_child_name(self.cb_active)
		except:
			self.conf_stack.set_visible_child_name("cpanel")
			
		self.update_alternatives=False	
		
	#def refresh_alternatives	
		
	def add_grid_button(self,grid_button):
		
		da=Gtk.DrawingArea()
		da.set_size_request(140,148)
		da.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK | Gdk.EventMask.BUTTON_PRESS_MASK )
		
		da.connect("draw",self.draw_button,grid_button)
		da.connect("motion-notify-event",self.mouse_over,grid_button)
		da.connect("leave_notify_event",self.mouse_left,grid_button)
		da.connect("button-press-event",self.button_clicked,grid_button)
		
		
		#button.connect("motion-notify-event",self.mouse_over,app,image)
		da.show()
		self.installers_grid.attach(da,self.current_grid_width,self.current_grid_height,1,1)
		
		self.current_grid_width+=1
		
		if self.current_grid_width > self.max_grid_width:
			self.current_grid_width=0
			self.current_grid_height+=1
			
	#def add_grid_button
	
	
	def conf_clicked(self,widget,event,cb):
		
		for item in self.conf_buttons:
			item.active=False
			item.da.queue_draw()
			
		cb.active=True
		self.cb_active=cb.name
		self.conf_stack.set_visible_child_name(cb.name)
		widget.queue_draw()
		
	#def conf_clicked
	
	
	def button_clicked(self,widget,event,grid_button):
		
		self.t=threading.Thread(target=self.execute,args=(grid_button.info["cmd"],))
		self.t.daemon=True
		self.t.start()
		GLib.timeout_add(100,self.pulsate_pbar,grid_button,widget)
		self.progress_window.show()
		
		
	#def button_clicked
	
	
	def draw_configure_button(self,widget,ctx,cb):
		
		if cb.active:
			ctx.set_source_rgba(self.conf_light.r,self.conf_light.g,self.conf_light.b,1)
			ctx.rectangle(0,0,110,123)
			ctx.fill()
			
			ctx.set_source_rgba(1,0,0,1)
			ctx.move_to(0,0)
			ctx.rectangle(0,1,5,121)
			ctx.fill()
			
		else:
			ctx.set_source_rgba(self.conf_dark.r,self.conf_dark.g,self.conf_dark.b,1)
			ctx.rectangle(0,0,110,123)
			ctx.fill()
		
		
		
		ctx.move_to(0,0)
		ctx.set_source_rgba(self.conf_light_shadow.r,self.conf_light_shadow.g,self.conf_light_shadow.b,1)
		ctx.rectangle(0,0,110,1)
		ctx.fill()
		
		ctx.move_to(0,0)
		ctx.set_source_rgba(self.conf_dark_shadow.r,self.conf_dark_shadow.g,self.conf_dark_shadow.b,1)
		ctx.rectangle(0,121,110,2)
		ctx.fill()
		
		ctx.move_to(0,0)
		img=cairo.ImageSurface.create_from_png(cb.icon)
		ctx.set_source_surface(img,33,22)
		ctx.paint()
		
		pctx = PangoCairo.create_layout(ctx)
		desc = Pango.font_description_from_string ("Quattrocento Sans Bold 10")
		pctx.set_font_description(desc)
		pctx.set_markup(cb.txt)
		ctx.set_source_rgba(self.light_gray.r,self.light_gray.g,self.light_gray.b,1)
		width=pctx.get_pixel_size()[0]
		ctx.move_to((110-width)/2,80)
		PangoCairo.show_layout(ctx, pctx)
		
	#def draw_configure_button
	

	def draw_button(self,widget,ctx,grid_button):
		
		ctx.move_to(0,0)
		img=cairo.ImageSurface.create_from_png(SHADOW_BANNER)
		ctx.set_source_surface(img,0,grid_button.info["shadow_start"])
		ctx.paint_with_alpha(grid_button.info["shadow_alpha"])
		
		ctx.move_to(0,0)
		img=cairo.ImageSurface.create_from_png(grid_button.info["image"])
		ctx.set_source_surface(img,0,0)
		ctx.paint()
		
		ctx.move_to(0,0)
		ctx.set_source_rgba(1,1,1,1)
		ctx.rectangle(0,110,140,30)
		ctx.fill()
		
		
		ctx.set_source_rgba(self.dark_gray.r,self.dark_gray.g,self.dark_gray.b,1)
		
		pctx = PangoCairo.create_layout(ctx)
		desc = Pango.font_description_from_string ("Quattrocento Sans Bold 10")
		pctx.set_font_description(desc)
		pctx.set_markup(grid_button.info["name"])
		ctx.move_to(5,118)
		PangoCairo.show_layout(ctx, pctx)
		width=pctx.get_pixel_size()[0]
		
		
		
		if grid_button.info["installed"]:
		
			desc = Pango.font_description_from_string ("Quattrocento Sans Bold 8")
			pctx.set_font_description(desc)
			ctx.set_source_rgba(self.green.r,self.green.g,self.green.b,1)
			txt=_("Installed")
			pctx.set_markup(txt)
			width=pctx.get_pixel_size()[0]
			ctx.move_to(140-width-5,120)
			PangoCairo.show_layout(ctx, pctx)
			
			
			#ctx.set_source_rgba(self.light_green.r,self.light_green.g,self.light_green.b,1)
			ctx.rectangle(5,139,130,1)
			ctx.fill()
		
		
	#def draw_button
	
	
	def drawing_label_event(self,widget,ctx,id):
		
		if id==self.current_tab:

			lg1 = cairo.LinearGradient(0.0,0.0, 300.0, 3.0)
			lg1.add_color_stop_rgba(0, 0, 1, 1, 0)
			lg1.add_color_stop_rgba(0.5, 0, 1, 1, 1)
			lg1.add_color_stop_rgba(1, 0, 1, 1, 0)
			ctx.rectangle(0, 0, 300, 3)
			ctx.set_source(lg1)
			ctx.fill()
			
	#drawing_label_event
	
	'''
	def draw_close_button(self,widget,ctx):
		
		
		button_border=22
		
		pctx = PangoCairo.create_layout(ctx)
		desc = Pango.font_description_from_string ("Quattrocento Sans Bold 12")
		pctx.set_font_description(desc)
		
		pctx.set_markup(_("CLOSE"))
		width=pctx.get_pixel_size()[0]
		widget.set_size_request(width+button_border*2,30)
		
		ctx.set_source_rgba(1,1,0,1)
		xx=0
		yx=0
		widthx=width+44
		heightx=30
		radius=5
		
		r=47.0
		g=167.0
		b=223.0
		alpha=1.0
		
		r=r/255.0
		g=g/255.0
		b=b/255.0
		
		r2=83
		g2=153
		b2=252
		
		r2=r2/255.0
		g2=g2/255.0
		b2=b2/255.0
		
		
		lg1 = cairo.LinearGradient(0.0,0.0, 90.0, 0)
		lg1.add_color_stop_rgba(0, r, g, b, 1)
		lg1.add_color_stop_rgba(1, r2, g2, b2, 1)
		ctx.set_source(lg1)
		
		
		ctx.move_to (xx + radius, yx);
		ctx.arc (xx + widthx - radius, yx + radius, radius, pi * 1.5, pi * 2);
		ctx.arc (xx + widthx - radius, yx + heightx - radius, radius, 0, pi * .5);
		ctx.arc (xx + radius, yx + heightx - radius, radius, pi * .5, pi);
		ctx.arc (xx + radius, yx + radius, radius, pi , pi * 1.5);
		ctx.fill ();
		
		ctx.set_source_rgb(0.9,0.9,0.9)
		ctx.move_to(button_border,7)
		PangoCairo.show_layout(ctx, pctx)
		
	#def draw_close_button
	'''

	
	def draw_top_divider(self,widget,ctx):
		
		r=self.light_gray.r
		g=self.light_gray.g
		b=self.light_gray.b
		alpha=1.0
		
		
		ctx.set_source_rgba(r,g,b,alpha)
		ctx.rectangle(0,1,510,3)
		ctx.fill()
		
		width=0

		if self.first_run:
		
			pctx = PangoCairo.create_layout(ctx)
			desc = Pango.font_description_from_string ("Quattrocento Sans Bold 18")
			pctx.set_font_description(desc)
			pctx.set_markup(_("Installers"))
			self.installers_width=pctx.get_pixel_size()[0]
			pctx.set_markup(_("Configuration"))
			self.configuration_width=pctx.get_pixel_size()[0]
			
			self.first_run=False
			
		if self.current_tab==0:
			width=self.installers_width
		else:
			width=self.configuration_width
		self.configuration_start=469-width
			
		ctx.set_source_rgba(1.0,0,0,alpha)
		
				
		if not self.animation_left and not self.animation_right:
		
			if self.current_tab==0:
				ctx.rectangle(0,0,width,3)
				
				self.current_red_width=width
				self.current_red_start=0
				
			else:
				ctx.rectangle(469-width,0,width,3)
				self.current_red_width=width
				self.current_red_start=469-width
			
			
			ctx.fill()
		
		else:
		
			ctx.rectangle(self.current_red_start,0,self.current_red_width,3)
			ctx.fill()
		
		
	#def draw_top_divider
	
	
	def draw_bottom_divider(self,widget,ctx):
		
		r=self.dark_gray.r
		g=self.dark_gray.g
		b=self.dark_gray.b
		alpha=1.0
		
		ctx.set_source_rgba(r,g,b,alpha)
		ctx.rectangle(0,1,500,3)
		ctx.fill()
		
	#def draw_bottom_divider
	
	
	def mouse_over(self,widget,event,grid_button):
		
		grid_button.info["animation_active"]=False
		if grid_button.info["shadow_alpha"] <0.5 :
			grid_button.info["shadow_alpha"]+=0.1
			widget.queue_draw()
			return True
			
		return False
		
	#def mouse_over

	
	def mouse_left(self,widget,event,grid_button):
		
		if not grid_button.info["animation_active"]:
			
			grid_button.info["animation_active"]=True
			GLib.timeout_add(10,self.restore_shadow_alpha,grid_button,widget)
			
	#def mouse_left

	
	def restore_shadow_alpha(self,grid_button,widget):

		if grid_button.info["shadow_alpha"] >0.2 :
			grid_button.info["shadow_alpha"]-=0.1
		
			
			widget.queue_draw()
			return True
			
		grid_button.info["animation_active"]=False
		return False
		
	#def  restore_shadow_alpha
	
	def update_divider_right(self):
		if self.configuration_width > self.installers_width:

			if self.current_red_width < self.configuration_width:
				self.current_red_width+=10
			if self.current_red_start < self.configuration_start:
				self.current_red_start+=10
			
			if self.current_red_width >= self.configuration_width and self.current_red_start >= self.configuration_start:
				self.animation_right=False
				
			self.top_divider_da.queue_draw()
			
		else:
			
			if self.current_red_width > self.configuration_width:
				self.current_red_width-=10
			if self.current_red_start < self.configuration_start:
				self.current_red_start+=10
			
			
			if self.current_red_width <= self.configuration_width and self.current_red_start >= self.configuration_start:
				
				self.animation_right=False
				
			self.top_divider_da.queue_draw()
		
		return self.animation_right
		
	#def update_divider_right
	
	def update_divider_left(self):
		
		
		if self.configuration_width > self.installers_width:

			if self.current_red_width > self.installers_width:
				self.current_red_width-=10
			if self.current_red_start > 0:
				self.current_red_start-=10
			
			
			if self.current_red_width <= self.installers_width and self.current_red_start <= 0:
				
				self.animation_left=False
				
			self.top_divider_da.queue_draw()
			
		else:
			
			if self.current_red_width < self.installers_width:
				self.current_red_width+=10
			if self.current_red_start > 0:
				self.current_red_start-=10
			
			
			if self.current_red_width >= self.installers_width and self.current_red_start <= 0:
				
				self.animation_left=False
				
			self.top_divider_da.queue_draw()
		
		return self.animation_left
		
	#def update_divider_left
	

	
	def label_clicked(self,widget,event,id):
		
		if id==0 and self.current_tab!=id:
			try:
				
				self.stack.set_visible_child_name("installers")
				self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
				self.installers_label.set_name("MAIN_LABEL_ENABLED")
				self.configuration_label.set_name("MAIN_LABEL_DISABLED")
				if not self.first_run:
					self.animation_left=True
					self.animation_right=False
					GLib.timeout_add(10,self.update_divider_left)
					
				
			except Exception as e:
				print e
		
		if id==1 and self.current_tab!=id:
			try:

				self.stack.set_visible_child_name("configuration")
				self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
				self.installers_label.set_name("MAIN_LABEL_DISABLED")
				self.configuration_label.set_name("MAIN_LABEL_ENABLED")
				self.animation_right=True
				self.animation_left=False
				GLib.timeout_add(10,self.update_divider_right)
				if self.update_alternatives:
					self.refresh_alternatives()
				
			except:
				pass
		
		self.current_tab=id
		
	#def label_clicked
	

	
#awesome tabs

if __name__=="__main__":
	
	at=AwesomeTabs()
