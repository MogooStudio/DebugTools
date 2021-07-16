import sys

from sql import SQLHelper
from sql import info, error

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTextEdit, QPushButton, QDialog, QToolButton, QRadioButton, QGroupBox, QStackedWidget, \
    QSizePolicy, QListWidgetItem, \
    QListWidget, \
    QWidget, QVBoxLayout, QHBoxLayout, QApplication, QMainWindow, \
    QMessageBox, QDesktopWidget

ui_title = "Slots工具"
ui_width = 1280
ui_height = 720
current_index = 0

item_width = 150
item_height = 80
item_titles = ["调试工具", "底包管理", "热更新管理", "资源包管理"]

# 自定义样式
ui_Stylesheet = """
    /*去掉item虚线边框*/
    QListWidget, QListView, QTreeWidget, QTreeView {
        outline: 0px;
    }
    /*设置左侧选项的最小最大宽度,文字颜色和背景颜色*/
    QListWidget {
        min-width: 120px;
        max-width: 120px;
        color: white;
        background: rgb(120, 120, 120);
    }
    /*被选中时的背景颜色和左边框颜色*/
    QListWidget::item:selected {
        background: rgb(110, 110, 110);
        border-left: 2px solid rgb(9, 187, 7);
    }
    /*鼠标悬停颜色*/
    HistoryPanel::item:hover {
        # background: rgb(52, 52, 52);
    }
    /*右侧的层叠窗口的背景颜色*/
    QStackedWidget {
        # background: rgb(30, 30, 30);
    }
    /*模拟的页面*/
    QLabel {
        # color: white;
    }
    """


# 基础dialog
class BaseDialog(QDialog):

    def __init__(self, width, height, name="BaseDialog"):
        super(BaseDialog, self).__init__()
        self.name = name
        self.width = width
        self.height = height
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.name)
        self.resize(self.width, self.height)


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


# 设置dialog
class PathSettingItem(QGroupBox):

    def __init__(self):
        super(PathSettingItem, self).__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QTextEdit())
        self.layout.addWidget(QPushButton("按钮"))
        self.setLayout(self.layout)


# 路径设置dialog
class PathSettingDialog(BaseDialog):

    def __init__(self):
        super(PathSettingDialog, self).__init__(800, 480, "设置")

    def initUI(self):
        super(PathSettingDialog, self).initUI()

        mainLayout = QVBoxLayout()
        for i in range(3):
            item = PathSettingItem()
            mainLayout.addWidget(item)

        self.setLayout(mainLayout)


# 左侧item控件
class ToolsItem(BaseItem):

    def __init__(self, name):
        super(ToolsItem, self).__init__(name)

    def initUI(self):
        super(ToolsItem, self).initUI()


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
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.listWidget = QListWidget()
        self.mainLayout.addWidget(self.listWidget)
        self.stackedWidget = QStackedWidget()
        self.mainLayout.addWidget(self.stackedWidget)
        self.toolBar = self.addToolBar("")
        self.toolBar.setMovable(False)
        self.initUI()
        self.db = SQLHelper()

    def initUI(self):
        self.initToolBar()

        # list widget
        self.listWidget.setFrameShape(QListWidget.NoFrame)
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding))
        self.listWidget.setMinimumSize(QSize(item_width, item_height))
        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)

        index = 0
        for title in item_titles:
            item = ToolsItem(title)
            item.setSizeHint(QSize(item_width, item_height))
            self.listWidget.addItem(item)
            index += 1

        # stacked widget
        index = 0
        for title in item_titles:
            view = ToolsView(title)
            self.stackedWidget.addWidget(view)
            index += 1

        # layout
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.resize(ui_width, ui_height)
        self.setPosition()
        self.setWindowTitle(ui_title)
        self.show()
        info("ui初始化成功")

    # 显示UI
    def showUI(self):
        self.listWidget.setCurrentRow(current_index)

    def initToolBar(self):
        width = 64
        btnSetting = QToolButton(self)
        btnSetting.setText('设置')
        btnSetting.setMinimumWidth(width)
        btnSetting.setIcon(QIcon('exit.png'))
        btnSetting.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        btnSetting.clicked.connect(self.showSettingDialog)
        self.toolBar.addWidget(btnSetting)

    def showSettingDialog(self):
        print("showSettingDialog")
        settingDialog = PathSettingDialog()
        settingDialog.exec_()

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
        if reply == QMessageBox.Yes:
            self.db.close()
            self.close()
        elif onerror:
            onerror()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(ui_Stylesheet)
    tools = DebugTools()
    tools.showUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
