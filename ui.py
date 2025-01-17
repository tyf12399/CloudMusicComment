# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cal
from cal import calculator
from time import sleep

class MyThr(QThread):
    def __init__(self, artist):
        self.artist = artist
        super().__init__()
    def run(self):
        self.mycal= calculator(self.artist)
        self.mycal.run()
    def draw(self):
        self.mycal.draw()

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(15, 71, 371, 221))
        self.textBrowser.setObjectName("textBrowser")
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setGeometry(QtCore.QRect(20, 30, 361, 28))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.lineEdit = QtWidgets.QLineEdit(self.splitter)
        self.lineEdit.setMaxLength(64)
        self.lineEdit.setReadOnly(False)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(self.splitter)
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        self.pushButton.setMouseTracking(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("search.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(16, 16))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Form)
        self.pushButton.clicked.connect(Form.getInput)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "网易云评论分析"))
        self.lineEdit.setPlaceholderText(_translate("Form", "输入歌手名称"))
        self.pushButton.setText(_translate("Form", "确定"))
    def getInput(self):
        cal.print = self.textBrowser.append
        artist = self.lineEdit.text()
        self.thr = MyThr(artist)
        self.thr.start()
        self.thr.finished.connect(self.thr.draw)

    

if __name__=='__main__':
    app=QApplication(sys.argv)
    win=Ui_MainWindow()
    win.show()
    sys.exit(app.exec_())
