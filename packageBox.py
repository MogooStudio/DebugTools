# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/jinshan/workspace/win/DebugTools/tools/../packageBox.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_packageBox(object):
    def setupUi(self, packageBox):
        packageBox.setObjectName("packageBox")
        packageBox.resize(1000, 600)
        packageBox.setMinimumSize(QtCore.QSize(1000, 600))
        packageBox.setTitle("")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(packageBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(packageBox)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 80))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 80))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(600, 40))
        self.widget.setMaximumSize(QtCore.QSize(500, 40))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.textEdit_hotUpdate = QtWidgets.QTextEdit(self.widget)
        self.textEdit_hotUpdate.setMaximumSize(QtCore.QSize(16777215, 25))
        self.textEdit_hotUpdate.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit_hotUpdate.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.textEdit_hotUpdate.setObjectName("textEdit_hotUpdate")
        self.horizontalLayout.addWidget(self.textEdit_hotUpdate)
        self.btn_select_dir = QtWidgets.QPushButton(self.widget)
        self.btn_select_dir.setObjectName("btn_select_dir")
        self.horizontalLayout.addWidget(self.btn_select_dir)
        self.btn_upload_files = QtWidgets.QPushButton(self.widget)
        self.btn_upload_files.setObjectName("btn_upload_files")
        self.horizontalLayout.addWidget(self.btn_upload_files)
        self.verticalLayout.addWidget(self.widget)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(packageBox)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2.addWidget(self.groupBox_2)

        self.retranslateUi(packageBox)
        QtCore.QMetaObject.connectSlotsByName(packageBox)

    def retranslateUi(self, packageBox):
        _translate = QtCore.QCoreApplication.translate
        packageBox.setWindowTitle(_translate("packageBox", "GroupBox"))
        self.groupBox.setTitle(_translate("packageBox", "上传热更新"))
        self.label.setText(_translate("packageBox", "资源包路径："))
        self.btn_select_dir.setText(_translate("packageBox", "选择"))
        self.btn_upload_files.setText(_translate("packageBox", "上传"))
        self.groupBox_2.setTitle(_translate("packageBox", "打包ipa"))
