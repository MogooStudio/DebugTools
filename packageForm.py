# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/jinshan/workspace/win/DebugTools/tools/../packageForm.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_packageForm(object):
    def setupUi(self, packageForm):
        packageForm.setObjectName("packageForm")
        packageForm.resize(1000, 600)
        packageForm.setMinimumSize(QtCore.QSize(1000, 600))
        self.tableWidget = QtWidgets.QTableWidget(packageForm)
        self.tableWidget.setGeometry(QtCore.QRect(15, 15, 970, 500))
        self.tableWidget.setMinimumSize(QtCore.QSize(970, 500))
        self.tableWidget.setShowGrid(True)
        self.tableWidget.setRowCount(3)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)

        self.retranslateUi(packageForm)
        QtCore.QMetaObject.connectSlotsByName(packageForm)

    def retranslateUi(self, packageForm):
        _translate = QtCore.QCoreApplication.translate
        packageForm.setWindowTitle(_translate("packageForm", "Form"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("packageForm", "git版本号"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("packageForm", "code版本号"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("packageForm", "发布状态"))
