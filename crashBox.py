# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\mogoo\workspace\python\DebugTools\tools\..\crashBox.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_crashBox(object):
    def setupUi(self, crashBox):
        crashBox.setObjectName("crashBox")
        crashBox.resize(299, 313)

        self.retranslateUi(crashBox)
        QtCore.QMetaObject.connectSlotsByName(crashBox)

    def retranslateUi(self, crashBox):
        _translate = QtCore.QCoreApplication.translate
        crashBox.setWindowTitle(_translate("crashBox", "Form"))
