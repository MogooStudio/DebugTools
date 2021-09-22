import sys
from enum import IntEnum

from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject
from PyQt5.QtWidgets import QHeaderView, QLineEdit, QComboBox, QTabWidget, QDialog, QGroupBox, \
    QListWidgetItem, QTableWidgetItem, \
    QWidget, QApplication, QMainWindow, \
    QMessageBox, QDesktopWidget

from mainUI import Ui_MainWindow
from groupForm import Ui_groupForm
from debugBox import Ui_debugBox
from packageBox import Ui_packageBox
from httpBox import Ui_httpBox
from sql import SQLHelper
from sql import info
from config import JsonConfig

is_debug = True


class ItemEnum(IntEnum):
    debug = 1
    ipa = 2
    http = 3
    end = 4


ui_title = "调试工具"
ui_width = 1280
ui_height = 720

item_width = 150
item_height = 80
item_titles = {
    ItemEnum.debug: "调试配置",
    ItemEnum.ipa: "打包ipa",
    ItemEnum.http: "http服务器",
}

tab_group_titles = ["game1", "game2", "game3"]

DATA_SAVE_PATH = "./"

DATA_BASE = {
    "project_path": "",
}

DATA_DEBUG = {
    "pad": False,
    "dialog": False,
    "download": False,
    "env": False,
    "splunk": False,
    "server": False,
}

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


# 左侧list项
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


# table项
class TableItem(QTableWidgetItem):

    def __init__(self, row, col):
        super(TableItem, self).__init__("TableItem")
        self.row = row
        self.col = col


# 调试项目框
class DebugBox(QGroupBox, Ui_debugBox):
    common_signal = pyqtSignal(dict)

    def __init__(self, parent):
        super(DebugBox, self).__init__()
        self.parent = parent
        self.selectPad = False
        self.selectDialog = False
        self.selectDownload = False
        self.selectEnv = False
        self.selectSplunk = False
        self.selectServer = 0
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        # mod btn
        self.btn_mod_game.clicked.connect(self.onClickedModBtn)
        # radio btn
        self.no_pad.setChecked(not self.selectPad)
        self.no_pad.toggled.connect(self.onSelectedPadBtn)
        self.no_dialog.setChecked(not self.selectDialog)
        self.no_dialog.toggled.connect(self.onSelectedDialogBtn)
        self.no_download.setChecked(not self.selectDownload)
        self.no_download.toggled.connect(self.onSelectedDownloadBtn)
        self.no_env.setChecked(not self.selectEnv)
        self.no_env.toggled.connect(self.onSelectedEnvBtn)
        self.no_splunk.setChecked(not self.selectSplunk)
        self.no_splunk.toggled.connect(self.onSelectedSplunkBtn)
        self.btn_server_path.setCurrentIndex(self.selectServer)
        self.btn_server_path.currentIndexChanged.connect(self.onSelectedServerBtn)

    def onSelectedPadBtn(self):
        self.selectPad = self.yes_pad.isChecked()
        if self.selectPad:
            info("打开模拟PAD")
        else:
            info("关闭模拟PAD")

    def onSelectedDialogBtn(self):
        self.selectDialog = self.yes_dialog.isChecked()
        if self.selectDialog:
            info("打开屏蔽弹窗")
        else:
            info("关闭屏蔽弹窗")

    def onSelectedDownloadBtn(self):
        self.selectDownload = self.yes_download.isChecked()
        if self.selectDownload:
            info("打开资源下载")
        else:
            info("关闭资源下载")

    def onSelectedEnvBtn(self):
        self.selectEnv = self.yes_env.isChecked()
        if self.selectEnv:
            info("打开外网环境")
        else:
            info("关闭外网环境")

    def onSelectedSplunkBtn(self):
        self.selectSplunk = self.yes_splunk.isChecked()
        if self.selectSplunk:
            info("打开强制打点")
        else:
            info("关闭强制打点")

    def onSelectedServerBtn(self, index):
        self.selectServer = index
        if index == 0:
            info("内网测试服务器")
        elif index == 1:
            info("外网测试服务器")
        elif index == 2:
            info("线上正式服务器")

    def getData(self):
        return {
            "game": self.parent.getGameGroup(),
            "path": self.parent.getRootPath(),
            "pad": self.selectPad,
            "dialog": self.selectDialog,
            "download": self.selectDownload,
            "env": self.selectEnv,
            "splunk": self.selectSplunk,
            "server": self.selectServer,
        }

    def onClickedModBtn(self):
        self.common_signal.emit(self.getData())


# 打包ipa框
class PackageBox(QGroupBox, Ui_packageBox):
    common_signal = pyqtSignal()

    def __init__(self, parent):
        super(PackageBox, self).__init__()
        self.parent = parent
        self.setupUi(self)


# http服务器框
class HttpServerBox(QGroupBox, Ui_httpBox):
    common_signal = pyqtSignal()

    def __init__(self, parent):
        super(HttpServerBox, self).__init__()
        self.parent = parent
        self.setupUi(self)


# game选择tab
class TabGroupView(QWidget, Ui_groupForm):
    common_signal = pyqtSignal(str)

    box_clz = {
        ItemEnum.debug: DebugBox,
        ItemEnum.ipa: PackageBox,
        ItemEnum.http: HttpServerBox,
    }

    def __init__(self, game):
        super(TabGroupView, self).__init__()
        self.game = game
        self.setupUi(self)
        self.initUI()
        self.btn_setting.clicked.connect(self.buttonClicked)

    def buttonClicked(self):
        self.common_signal.emit(self.getRootPath())

    def initUI(self):
        itemEnum = ItemEnum(1)
        for title in item_titles.values():
            item = ListItem(title)
            item.setSizeHint(QSize(item_width, item_height))
            self.listWidget.addItem(item)
            itemEnum += 1

    def addBox(self, enum, handle):
        box = self.box_clz[enum](self)
        box.common_signal.connect(handle)
        self.stackedWidget.addWidget(box)

    def setCurrentRow(self):
        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)
        self.listWidget.setCurrentRow(0)

    def getGameGroup(self):
        return self.game

    def getRootPath(self):
        return sys.path[0] + "/" + self.game


class DebugTools(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(DebugTools, self).__init__()
        # self.config = JsonConfig()
        self.handle = {
            ItemEnum.debug: self.saveDebug,
            ItemEnum.ipa: self.packageIPA,
            ItemEnum.http: self.createServer,
        }
        self.setupUi(self)
        self.init()

    def init(self):
        self.initData()
        self.initUI()

    def initData(self):
        info("加载数据")

    def initUI(self):
        for title in tab_group_titles:
            tabView = TabGroupView(title)
            itemEnum = ItemEnum(1)
            for _ in item_titles.values():
                tabView.addBox(itemEnum, self.handle[itemEnum])
                itemEnum += 1
            tabView.setCurrentRow()
            tabView.common_signal.connect(self.setProjectRoot)
            self.tabWidget.addTab(tabView, title)

        self.resize(ui_width, ui_height)
        frame = self.frameGeometry()
        frame.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())
        self.setWindowTitle(ui_title)
        info("初始化UI")

    def setProjectRoot(self, path):
        info(path)

    def saveDebug(self, data):
        info(data)

    def packageIPA(self):
        info("打包ipa")

    def createServer(self):
        info("创建http服务器")

    def destroy(self):
        self.saveData()
        self.close()

    def closeEvent(self, event):
        if is_debug:
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
    # app.setStyleSheet(ui_Stylesheet)
    tools = DebugTools()
    tools.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
