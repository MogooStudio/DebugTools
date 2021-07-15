import sys
from PyQt5.QtWidgets import QToolButton, QRadioButton, QGroupBox, QStackedLayout, QSizePolicy, QListWidgetItem, QListWidget, \
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QAction, QApplication, QMainWindow, \
    QMessageBox, QLabel, QLineEdit, QTextEdit, QPushButton, QDesktopWidget
from PyQt5.QtCore import Qt, QCoreApplication, QSize
from PyQt5.QtGui import QIcon, QColor

ui_title = "Slots工具"
ui_width = 1280
ui_height = 720
current_index = 0

item_width = 150
item_height = 80
item_titles = ["调试工具", "底包管理", "热更新管理", "资源包管理"]


# 基础Item
class BaseItem(QListWidgetItem):

    def __init__(self, name="BaseItem"):
        super(BaseItem, self).__init__()
        self.index = 0
        self.name = name
        self.initUI()

    def initUI(self):
        print(self.name + ":initUI")
        self.setText(self.name)

    def setIndex(self, index):
        self.index = index

    def getIndex(self):
        return self.index

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name


# 基础View
class BaseView(QGroupBox):

    def __init__(self, name="BaseView"):
        super(BaseView, self).__init__(name)
        self.index = 0
        self.name = name
        self.initUI()

    def initUI(self):
        print(self.name + ":initUI")

    def setIndex(self, index):
        self.index = index

    def getIndex(self):
        return self.index

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name


# 左侧item控件
class ToolsItem(BaseItem):

    def __init__(self, name):
        super(ToolsItem, self).__init__(name)

    def initUI(self):
        super(ToolsItem, self).initUI()
        self.setBackground(QColor(100, 100, 100, 100))


# 右侧view控件
class ToolsView(BaseView):

    def __init__(self, name):
        super(ToolsView, self).__init__(name)

    def initUI(self):
        radio1 = QRadioButton('&Radio Button 1')
        radio2 = QRadioButton('R&adio button 2')
        radio3 = QRadioButton('Ra&dio button 3')

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(radio1)
        self.layout.addWidget(radio2)
        self.layout.addWidget(radio3)
        self.layout.addStretch(1)
        self.setLayout(self.layout)


class DebugTools(QMainWindow):

    def __init__(self):
        super(DebugTools, self).__init__()
        self.mainWidget = QWidget()
        self.mainLayout = QHBoxLayout()
        self.listWidget = QListWidget()
        self.rightWidget = QWidget()
        self.rightLayout = QStackedLayout(self.rightWidget)
        self.toolBar = self.addToolBar("")
        self.initUI()

    def initUI(self):
        self.initToolBar()

        # listview
        self.listWidget.setSpacing(10)
        self.listWidget.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding))
        self.listWidget.setMinimumSize(QSize(item_width, item_height))
        self.listWidget.clicked.connect(self.onClickedItem)
        self.mainLayout.addWidget(self.listWidget)

        # right view
        self.rightWidget.setLayout(self.rightLayout)
        self.mainLayout.addWidget(self.rightWidget)

        index = 0
        for title in item_titles:
            item = ToolsItem(title)
            item.setSizeHint(QSize(item_width, item_height))
            self.listWidget.addItem(item)
            view = ToolsView(title)
            self.rightLayout.addWidget(view)
            index += 1

        # layout
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.resize(ui_width, ui_height)
        self.setPosition()
        self.setWindowTitle(ui_title)
        self.show()

    # 显示UI
    def showUI(self):
        self.listWidget.setCurrentRow(current_index)
        self.changeView(current_index)

    def initToolBar(self):
        width = 64
        btnSetting = QToolButton(self)
        btnSetting.setText('设置')
        btnSetting.setMinimumWidth(width)
        btnSetting.setIcon(QIcon('exit.png'))
        btnSetting.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        btnSetting.clicked.connect(self.showSettingDialog)
        self.toolBar.addWidget(btnSetting)

    # 切换右侧view
    def changeView(self, index):
        if index < self.rightLayout.count():
            self.rightLayout.setCurrentIndex(index)
            widget = self.rightLayout.currentWidget()
            print(ToolsView(widget).name)
            print("选择：{0}".format(item_titles[index]))

    # 左侧item点击回调
    def onClickedItem(self, data):
        index = data.row()
        self.changeView(index)

    def showSettingDialog(self):
        print("showSettingDialog")
        # filename = QFileDialog.getOpenFileName(self, '打开文件', './')
        # if filename[0]:
        #     f = open(filename[0], 'r')
        #     with f:
        #         data = f.read()
        #         print(data)

    def setPosition(self):
        frame = self.frameGeometry()
        frame.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())

    def closeEvent(self, event):
        self.closeUI(lambda: event.ignore())

    def closeUI(self, onerror):
        reply = QMessageBox.question(self, '消息框', "确定关闭程序？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        self.close() if reply == QMessageBox.Yes else onerror()


def main():
    app = QApplication(sys.argv)
    tools = DebugTools()
    tools.showUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
