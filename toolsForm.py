# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'toolsForm.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_toolsForm(object):
    def setupUi(self, toolsForm):
        toolsForm.setObjectName("toolsForm")
        toolsForm.resize(1280, 720)
        toolsForm.setMinimumSize(QtCore.QSize(1280, 720))
        toolsForm.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout = QtWidgets.QVBoxLayout(toolsForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.contentView = QtWidgets.QWidget(toolsForm)
        self.contentView.setObjectName("contentView")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.contentView)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listWidget = QtWidgets.QListWidget(self.contentView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setMinimumSize(QtCore.QSize(200, 0))
        self.listWidget.setMaximumSize(QtCore.QSize(200, 16777215))
        self.listWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget.setObjectName("listWidget")
        self.horizontalLayout.addWidget(self.listWidget)
        self.stackedWidget = QtWidgets.QStackedWidget(self.contentView)
        self.stackedWidget.setObjectName("stackedWidget")
        self.horizontalLayout.addWidget(self.stackedWidget)
        self.verticalLayout.addWidget(self.contentView)

        self.retranslateUi(toolsForm)
        self.stackedWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(toolsForm)

    def retranslateUi(self, toolsForm):
        _translate = QtCore.QCoreApplication.translate
        toolsForm.setWindowTitle(_translate("toolsForm", "Form"))
