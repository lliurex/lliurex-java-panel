#!/usr/bin/python3
import os
import sys
from PySide6 import QtCore, QtGui, QtQml

class JavasModel(QtCore.QAbstractListModel):

	PkgRole= QtCore.Qt.UserRole + 1000
	IsCheckedRole=QtCore.Qt.UserRole+1002
	NameRole=QtCore.Qt.UserRole+1003
	BannerRole=QtCore.Qt.UserRole+1004
	StatusRole=QtCore.Qt.UserRole+1005
	IsVisibleRole=QtCore.Qt.UserRole+1006
	ResultProcessRole=QtCore.Qt.UserRole+1007
	ShowSpinnerRole = QtCore.Qt.UserRole + 1008
	IsManagedRole=QtCore.Qt.UserRole+1009


	def __init__(self,parent=None):
		
		super(JavasModel, self).__init__(parent)
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
			if role == JavasModel.PkgRole:
				return item["pkg"]
			elif role == JavasModel.IsCheckedRole:
				return item["isChecked"]
			elif role == JavasModel.NameRole:
				return item["name"]
			elif role == JavasModel.BannerRole:
				return item["banner"]
			elif role == JavasModel.StatusRole:
				return item["status"]
			elif role == JavasModel.IsVisibleRole:
				return item["isVisible"]
			elif role == JavasModel.ResultProcessRole:
				return item["resultProcess"]
			elif role == JavasModel.ShowSpinnerRole:
				return item["showSpinner"]
			elif role == JavasModel.IsManagedRole:
				return item["isManaged"]
		
		#def data

	def roleNames(self):
		
		roles = dict()
		roles[JavasModel.PkgRole] = b"pkg"
		roles[JavasModel.IsCheckedRole] = b"isChecked"
		roles[JavasModel.NameRole] = b"name"
		roles[JavasModel.BannerRole] = b"banner"
		roles[JavasModel.StatusRole] = b"status"
		roles[JavasModel.IsVisibleRole] = b"isVisible"
		roles[JavasModel.ResultProcessRole] = b"resultProcess"
		roles[JavasModel.ShowSpinnerRole] = b"showSpinner"
		roles[JavasModel.IsManagedRole]=b"isManaged"

		return roles

	#def roleName

	def appendRow(self,pkg,na,isc,st,ba,isv,rpr,ss,im):
		
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
		self._entries.append(dict(pkg=pkg, name=na,isChecked=isc,status=st,banner=ba,isVisible=isv,resultProcess=rpr,showSpinner=ss,isManaged=im))
		self.endInsertRows()

	#def appendRow

	def setData(self, index, valuesToUpdate, role=QtCore.Qt.EditRole):
		
		if role == QtCore.Qt.EditRole:
			row = index.row()
			for item in valuesToUpdate:
				for param in item:
					if param in ["status","showSpinner","isVisible","isChecked","resultProcess"]:
						self._entries[row][param]=item[param]
						self.dataChanged.emit(index,index)

	#def setData

	def clear(self):
		
		count=self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class JavasModel
