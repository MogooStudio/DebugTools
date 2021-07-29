import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QHeaderView, QLineEdit, QComboBox, QTabWidget, QDialog, QGroupBox, \
    QListWidgetItem, QTableWidgetItem, \
    QWidget, QApplication, QMainWindow, \
    QMessageBox, QDesktopWidget


from mainUI import Ui_MainWindow
from groupForm import Ui_groupForm
from debugBox import Ui_debugBox
from packageBox import Ui_packageBox
from packageForm import Ui_packageForm
from sql import SQLHelper
from sql import info

debug = True

ui_title = "调试工具"
ui_width = 1280
ui_height = 720

item_width = 150
item_height = 80
item_titles = ["调试配置", "底包管理", "热更新管理", "资源包管理"]

tab_group_titles = ["game1", "game2", "game3"]
tab_platform_titles = ["android", "ios"]

table_titles = ["git版本号", "code版本号", "发布状态"]
table_cols = len(table_titles)
table_rows = 20

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

    def __init__(self, name="DebugBox"):
        super(DebugBox, self).__init__()
        self.name = name
        self.setupUi(self)


# 底包管理框
class PackageBox(QTabWidget, Ui_packageBox):

    def __init__(self, name="PackageBox"):
        super(PackageBox, self).__init__()
        self.name = name
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        index = 0
        for title in tab_platform_titles:
            self.addTab(TabPlatformView(), title)
            index += 1


# game选择tab
class TabGroupView(QWidget, Ui_groupForm):

    def __init__(self):
        super(TabGroupView, self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):

        index = 0
        for title in item_titles:
            item = ListItem(title)
            item.setSizeHint(QSize(item_width, item_height))
            self.listWidget.addItem(item)

            if index == 0:
                self.stackedWidget.addWidget(DebugBox(item_titles[index]))
            else:
                self.stackedWidget.addWidget(PackageBox(item_titles[index]))

            index += 1

        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)
        self.listWidget.setCurrentRow(0)


# 平台选择tab
class TabPlatformView(QWidget, Ui_packageForm):

    def __init__(self):
        super(TabPlatformView, self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):

        self.tableWidget.setColumnCount(table_cols)
        self.tableWidget.setRowCount(table_rows)

        index = 0
        for name in table_titles:
            self.tableWidget.setHorizontalHeaderItem(index, QTableWidgetItem(name))
            index += 1

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # versionVal = QLineEdit('0.0')
        # versionVal.setAlignment(Qt.AlignHCenter)
        # self.tableWidget.setCellWidget(0, 0, versionVal)
        #
        # versionVal = QLineEdit('0.0')
        # versionVal.setAlignment(Qt.AlignHCenter)
        # self.tableWidget.setCellWidget(0, 1, versionVal)

        item = self.tableWidget.itemAt(1, 1)
        item.setText("111")

        for row in range(table_rows):
            cmbState = QComboBox()
            cmbState.addItem('审核中')
            cmbState.addItem('已发布')
            cmbState.addItem('已废弃')
            cmbState.setCurrentIndex(0)
            self.tableWidget.setCellWidget(row, 2, cmbState)


class DebugTools(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(DebugTools, self).__init__()
        self.db = SQLHelper()
        self.setupUi(self)
        self.init()

    def init(self):
        self.initData()
        self.initUI()

    def initData(self):
        info("加载数据")

    def initUI(self):
        index = 0
        for title in tab_group_titles:
            self.tabWidget.addTab(TabGroupView(), title)
            index += 1

        self.resize(ui_width, ui_height)
        frame = self.frameGeometry()
        frame.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())
        self.setWindowTitle(ui_title)
        info("初始化UI")

    def saveData(self):
        info("保存数据")

    def destroy(self):
        self.saveData()
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
    # app.setStyleSheet(ui_Stylesheet)
    tools = DebugTools()
    tools.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
