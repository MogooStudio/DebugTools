# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'packageCheckBox.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_packageCheckBox(object):
    def setupUi(self, packageCheckBox):
        packageCheckBox.setObjectName("packageCheckBox")
        packageCheckBox.resize(1000, 600)
        packageCheckBox.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(12)
        packageCheckBox.setFont(font)
        packageCheckBox.setTitle("")
        self.gridLayout_2 = QtWidgets.QGridLayout(packageCheckBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(packageCheckBox)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea = QtWidgets.QScrollArea(self.groupBox)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 631, 50000))
        self.scrollAreaWidgetContents.setMinimumSize(QtCore.QSize(631, 50000))
        self.scrollAreaWidgetContents.setMaximumSize(QtCore.QSize(631, 50000))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label.setGeometry(QtCore.QRect(0, 0, 631, 50000))
        self.label.setMinimumSize(QtCore.QSize(631, 50000))
        self.label.setMaximumSize(QtCore.QSize(631, 50000))
        self.label.setText("")
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.gridLayout_2.addWidget(self.groupBox, 1, 0, 1, 1)
        self.groupBox_5 = QtWidgets.QGroupBox(packageCheckBox)
        self.groupBox_5.setMinimumSize(QtCore.QSize(300, 0))
        self.groupBox_5.setMaximumSize(QtCore.QSize(300, 16777215))
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.btn_check = QtWidgets.QPushButton(self.groupBox_5)
        self.btn_check.setObjectName("btn_check")
        self.verticalLayout_3.addWidget(self.btn_check)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.gridLayout_2.addWidget(self.groupBox_5, 1, 1, 1, 1)
        self.widget = QtWidgets.QWidget(packageCheckBox)
        self.widget.setMinimumSize(QtCore.QSize(0, 50))
        self.widget.setMaximumSize(QtCore.QSize(16777215, 50))
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.textEdit = QtWidgets.QTextEdit(self.widget)
        self.textEdit.setMinimumSize(QtCore.QSize(0, 25))
        self.textEdit.setMaximumSize(QtCore.QSize(16777215, 25))
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setReadOnly(True)
        self.textEdit.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.textEdit.setObjectName("textEdit")
        self.horizontalLayout_2.addWidget(self.textEdit)
        self.pushButton = QtWidgets.QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 2)

        self.retranslateUi(packageCheckBox)
        QtCore.QMetaObject.connectSlotsByName(packageCheckBox)

    def retranslateUi(self, packageCheckBox):
        _translate = QtCore.QCoreApplication.translate
        packageCheckBox.setWindowTitle(_translate("packageCheckBox", "GroupBox"))
        self.groupBox.setTitle(_translate("packageCheckBox", "输出结果"))
        self.groupBox_5.setTitle(_translate("packageCheckBox", "功能列表"))
        self.btn_check.setText(_translate("packageCheckBox", "开始检测"))
        self.label_2.setText(_translate("packageCheckBox", "游戏包路径："))
        self.textEdit.setPlaceholderText(_translate("packageCheckBox", "点击[打开]选择游戏包..."))
        self.pushButton.setText(_translate("packageCheckBox", "打开"))
