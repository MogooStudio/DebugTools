# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\mogoo\workspace\Python\DebugTools\tools\..\groupForm.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_groupForm(object):
    def setupUi(self, groupForm):
        groupForm.setObjectName("groupForm")
        groupForm.resize(1280, 720)
        groupForm.setMinimumSize(QtCore.QSize(1280, 720))
        groupForm.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout = QtWidgets.QVBoxLayout(groupForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gameView = QtWidgets.QWidget(groupForm)
        self.gameView.setMinimumSize(QtCore.QSize(0, 50))
        self.gameView.setMaximumSize(QtCore.QSize(16777215, 50))
        self.gameView.setObjectName("gameView")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.gameView)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_title = QtWidgets.QLabel(self.gameView)
        self.label_title.setObjectName("label_title")
        self.horizontalLayout_2.addWidget(self.label_title, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.textEdit_path = QtWidgets.QTextEdit(self.gameView)
        self.textEdit_path.setMinimumSize(QtCore.QSize(400, 25))
        self.textEdit_path.setMaximumSize(QtCore.QSize(400, 25))
        self.textEdit_path.setObjectName("textEdit_path")
        self.horizontalLayout_2.addWidget(self.textEdit_path, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.btn_setting = QtWidgets.QPushButton(self.gameView)
        self.btn_setting.setObjectName("btn_setting")
        self.horizontalLayout_2.addWidget(self.btn_setting, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.verticalLayout.addWidget(self.gameView, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.contentView = QtWidgets.QWidget(groupForm)
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
        self.contentView.raise_()
        self.gameView.raise_()

        self.retranslateUi(groupForm)
        self.stackedWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(groupForm)

    def retranslateUi(self, groupForm):
        _translate = QtCore.QCoreApplication.translate
        groupForm.setWindowTitle(_translate("groupForm", "Form"))
        self.label_title.setText(_translate("groupForm", "项目路径:"))
        self.btn_setting.setText(_translate("groupForm", "设置"))
