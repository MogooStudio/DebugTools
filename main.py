import sys

from sql import SQLHelper
from sql import info, error

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QTabWidget, QTextEdit, QPushButton, QDialog, QToolButton, QRadioButton, QGroupBox, \
    QStackedWidget, \
    QSizePolicy, QListWidgetItem, \
    QListWidget, \
    QWidget, QVBoxLayout, QHBoxLayout, QApplication, QMainWindow, \
    QMessageBox, QDesktopWidget

from ui import Ui_MainWindow
from tabUI import Ui_tabForm
from contentBox import Ui_ContentBox
from debugBox import  Ui_debugBox

debug = True

ui_title = "调试工具"
ui_width = 1280
ui_height = 720
current_index = 0

game_max_height = 100

item_width = 150
item_height = 80
item_titles = ["调试配置", "底包管理", "热更新管理", "资源包管理"]

game_group = ["game1", "game2", "game3"]

# 自定义样式
ui_Stylesheet = """
    /*去掉一些控件虚线边框*/
    QListWidget, QListView, QTreeWidget, QTreeView {
        outline: 0px;
    }
    /*设置QListWidget选项的文字颜色和背景颜色*/
    QListWidget {
        color: white;
        background: rgb(120, 120, 120);
    }
    /*设置QListWidget被选中时的背景颜色和左边框颜色*/
    QListWidget::item:selected {
        background: rgb(110, 110, 110);
        border-left: 2px solid rgb(9, 187, 7);
    }
    /*设置鼠标悬停颜色*/
    HistoryPanel::item:hover {
        # background: rgb(52, 52, 52);
    }
    /*设置QStackedWidget的背景颜色*/
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

    def __init__(self, width, height, name=""):
        super(BaseDialog, self).__init__()
        self.name = name
        self.width = width
        self.height = height
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.name)
        self.resize(self.width, self.height)


# 基础View
class BaseView(QGroupBox):

    def __init__(self, index=0, name=""):
        super(BaseView, self).__init__(name)
        self.index = index
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


class GameView(QWidget):

    def __init__(self, index, name):
        super(GameView, self).__init__()
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()

        labWidget = QWidget()
        labWidget.setMinimumHeight(50)
        btnWidget = QWidget()
        btnWidget.setMinimumHeight(50)
        mainLayout.addWidget(labWidget)
        mainLayout.addWidget(btnWidget)

        labTitle = QLabel()
        labTitle.setMaximumWidth(100)
        labTitle.setText("项目路径: ")
        textEdit = QTextEdit()
        textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        textEdit.setMaximumSize(QSize(500, 25))

        labLayout = QHBoxLayout()
        labLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        labLayout.addWidget(labTitle)
        labLayout.addWidget(textEdit)

        btnLayout = QHBoxLayout()
        btnLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        for i in range(5):
            btnLayout.addWidget(QPushButton("按钮"))

        labWidget.setLayout(labLayout)
        btnWidget.setLayout(btnLayout)
        self.setLayout(mainLayout)


# 右侧ContentView
class ContentView(BaseView):

    def __init__(self, index):
        super(ContentView, self).__init__(index)

    def initUI(self):
        radio1 = QRadioButton('Radio Button 1')
        radio2 = QRadioButton('Radio button 2')
        radio3 = QRadioButton('Radio button 3')

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(radio1)
        mainLayout.addWidget(radio2)
        mainLayout.addWidget(radio3)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


# 左侧listItem
class ListItem(QListWidgetItem):

    def __init__(self, name):
        super(ListItem, self).__init__()
        self.name = name
        self.initUI()

    def initUI(self):
        self.setTextAlignment(Qt.AlignCenter)
        self.refreshUI()

    def refreshUI(self):
        self.setText(self.name)

    def setName(self, name):
        self.name = name
        self.refreshUI()


class DebugBox(QGroupBox, Ui_debugBox):

    def __init__(self, name):
        super(DebugBox, self).__init__()
        self.name = name
        self.setupUi(self)


# 程序ui框：tabWidget
class TabView(QWidget, Ui_tabForm):

    def __init__(self):
        super(TabView, self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):

        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)

        index = 0
        for title in item_titles:
            item = ListItem(title)
            item.setSizeHint(QSize(item_width, item_height))
            self.listWidget.addItem(item)
            index += 1

        index = 0
        for title in item_titles:
            view = DebugBox(title)
            self.stackedWidget.addWidget(view)
            index += 1


class DebugTools(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(DebugTools, self).__init__()
        self.setupUi(self)
        self.initUI()
        self.db = SQLHelper()

    def initUI(self):

        index = 0
        for name in game_group:
            self.tabWidget.addTab(TabView(), name)
            index += 1

        self.resize(ui_width, ui_height)
        self.setPosition()
        self.setWindowTitle(ui_title)
        info("ui初始化成功")

    # 添加tab
    def createTab(self, index):
        if index < 0 or index >= len(game_group):
            raise Exception("createTab: index > 0 and index < len(game_group)")

        mainWidget = QWidget()
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # 上下 layout
        gameView = GameView(index, game_group[index])
        gameView.setMaximumHeight(game_max_height)
        secondWidget = QWidget()
        secondWidget.setMinimumSize(QSize(ui_width, 10))
        mainLayout.addWidget(gameView)
        mainLayout.addWidget(secondWidget)

        # 左右 layout
        secondLayout = QHBoxLayout()
        secondWidget.setLayout(secondLayout)

        listWidget = QListWidget()
        stackedWidget = QStackedWidget()
        secondLayout.addWidget(listWidget)
        secondLayout.addWidget(stackedWidget)

        # list widget
        listWidget.setFrameShape(QListWidget.NoFrame)
        listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        listWidget.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding))
        listWidget.setMinimumSize(QSize(item_width, item_height))
        listWidget.currentRowChanged.connect(stackedWidget.setCurrentIndex)

        index = 0
        for title in item_titles:
            item = ListItem(index, title)
            item.setSizeHint(QSize(item_width, item_height))
            listWidget.addItem(item)
            index += 1

        # stack widget
        index = 0
        for _ in item_titles:
            view = ContentView(index)
            stackedWidget.addWidget(view)
            index += 1

        listWidget.setCurrentRow(0)
        mainWidget.setLayout(mainLayout)
        return mainWidget

    def setPosition(self):
        frame = self.frameGeometry()
        frame.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())

    def destroy(self):
        self.db.close()
        self.close()

    def closeEvent(self, event):
        if debug:
            self.destroy()
        else:
            self.closeUI(lambda: event.ignore())

    def closeUI(self, onerror):
        reply = QMessageBox.question(self, '消息框', "确定关闭程序？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.destroy()
        elif onerror:
            onerror()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(ui_Stylesheet)
    tools = DebugTools()
    tools.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
