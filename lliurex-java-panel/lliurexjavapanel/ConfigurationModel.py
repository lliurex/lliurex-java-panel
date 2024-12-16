#!/usr/bin/python3
import os
import sys
from PySide6 import QtCore, QtGui, QtQml

class ConfigurationModel(QtCore.QAbstractListModel):

	IdRole= QtCore.Qt.UserRole + 1000
	BannerRole=QtCore.Qt.UserRole+1001
	

	def __init__(self,parent=None):
		
		super(ConfigurationModel, self).__init__(parent)
		self._entries =[]
	
	#def __init__

	def rowCount(self, parent=QtCore.QModelIndex()):
		
		if parent.isValid():
			return 0
		return len(self._entries)

	#def rowCount

	def data(self, index, role=QtCore.Qt.DisplayRole):
		
		if 0 <= index.row() < self.rowCount() and index.isValid():
			item = self._entries[index.row()]
			if role == ConfigurationModel.IdRole:
				return item["id"]
			elif role == ConfigurationModel.BannerRole:
				return item["banner"]
		#def data

	def roleNames(self):
		
		roles = dict()
		roles[ConfigurationModel.IdRole] = b"id"
		roles[ConfigurationModel.BannerRole] = b"banner"
	
		return roles

	#def roleName

	def appendRow(self,id,ba):
		
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
		self._entries.append(dict(id=id,banner=ba))
		self.endInsertRows()

	#def appendRow

	def clear(self):
		
		count=self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class ConfigurationModel
