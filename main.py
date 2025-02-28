import base64
import os
import sys
import plistlib
import shutil
import threading
from enum import IntEnum
from random import sample

from PyQt5.QtGui import QPixmap, QDesktopServices, QIcon, QColor, QPainterPath, QPainter, QImage, QDragEnterEvent, \
    QDropEvent, QIntValidator, QRegExpValidator
from PyQt5.QtCore import QSize, pyqtSignal, QUrl, QStandardPaths, QTimer, QRectF, Qt, QRegExp
from PyQt5.QtWidgets import QSpacerItem, QListWidget, QLabel, QGridLayout, QHBoxLayout, QFileDialog, QDialog, \
    QGroupBox, QListWidgetItem, \
    QWidget, QApplication, QMainWindow, \
    QMessageBox, QDesktopWidget, QGraphicsDropShadowEffect, QSizePolicy
from dexparser import AABParser, APKParser

from aboutDialog import Ui_aboutDialog
from codeCheckBox import Ui_codeCheckBox
from ipaBox import Ui_ipaBox
from ipsBox import Ui_ipsBox
from keyRandomBox import Ui_keyRandomBox
from mainUI import Ui_MainWindow
from crashBox import Ui_crashBox

from log import LogHelper
from packageCheckBox import Ui_packageCheckBox
from resCheckBox import Ui_resCheckBox
from toolsForm import Ui_toolsForm


# 全局函数
def MakeDir(dirPath):
    if dirPath and not os.path.exists(dirPath):
        os.makedirs(dirPath)


def OpenDir(dirPath):
    if IS_MAC:
        os.system("open " + dirPath)
    else:
        QDesktopServices.openUrl(QUrl(dirPath))


def WritFile(filename, content):
    try:
        with open(filename, "w", encoding='utf-8') as fp:
            fp.write(content)
    except Exception as ex:
        LOG.error("写入文件失败：{0}, {1}".format(filename, ex))


def ReadFile(filename):
    try:
        with open(filename, "r", encoding='utf-8') as fp:
            return fp.read()
    except Exception as ex:
        LOG.error("读取文件失败：{0}, {1}".format(filename, ex))


def ReadPlist(filename):
    try:
        with open(filename, "rb", encoding='utf-8') as fp:
            return plistlib.load(fp)
    except Exception as ex:
        LOG.error("读取plist失败：{0}, {1}".format(filename, ex))


def CheckProject(path):
    res_dir = path + "/res"
    src_dir = path + "/src"
    return path and path != "" and os.path.exists(res_dir) and os.path.exists(src_dir)


# 全局变量
IS_DEBUG_MODE = True
IS_MAC = sys.platform == "darwin"
USER_PATH = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
WORK_PATH = USER_PATH + "/.debugtools"
MakeDir(WORK_PATH)
LOG_PATH = WORK_PATH + "/log"
MakeDir(LOG_PATH)
TEMP_PATH = WORK_PATH + "/temp"
MakeDir(TEMP_PATH)


log_config = {
    "log_path": LOG_PATH,
    "backup_count": 10,
}
LOG = LogHelper(log_config)

UI_WIDTH = 1298
UI_HEIGHT = 900
ITEM_WIDTH = 150
ITEM_HEIGHT = 80

UI_TITLE = "Mogoo工具集"
ERROR_TITLE = "错误"
WARN_TITLE = "警告"
PROMPT_TITLE = "提示"

PACKAGE_CHECK_WORDS = [
    'inmobi',
]

CODE_CHECK_WORDS = [
    'inmobi',
    'audit',
    'Audit',
    'AUDIT',
    'auditing',
    'AUDITING',
    'hotupdate',
    'hotUpdate',
    'Hotupdate',
    'HotUpdate',
    'HOTUPDATE',
    '热更',
    'induce',
    'Induce',
    'INDUCE',
    'Migrate',
    'tort',
    'TortShield',
    'Tort',
    '提审',
    'NEW_GP_PACK',
    '诱导',
    '审核',
    '侵权',
]

# 枚举
class ToolsItemEnum(IntEnum):
    packageCheck = 1
    codeCheck = 2
    resCheck = 3
    keyRandom = 4
    ipa = 5
    ips = 6


class MessageError(IntEnum):
    not_exist_path = 1
    config_lua = 2
    no_key = 3
    error_param = 4


class MessageWarn(IntEnum):
    package_release = 1
    check_running = 2


class CrashBoxEnum(IntEnum):
    ips = 1
    dSYM = 2


tools_item_titles = {
    ToolsItemEnum.packageCheck: "游戏包检测",
    ToolsItemEnum.codeCheck: "代码检测",
    ToolsItemEnum.resCheck: "资源加密检测",
    ToolsItemEnum.keyRandom: "密钥生成",
    ToolsItemEnum.ipa: "ipa打包",
    ToolsItemEnum.ips: "崩溃解析",
}

crash_titles = {
    CrashBoxEnum.ips: "把ips拖入到框内",
    CrashBoxEnum.dSYM: "把ips拖入到框内",
}

crash_suffix = {
    CrashBoxEnum.ips: ".ips",
    CrashBoxEnum.dSYM: ".dSYM",
}

message_error = {
    MessageError.config_lua: "配置文件selfConfig不存在",
    MessageError.not_exist_path: "路径不存在",
    MessageError.no_key: "key不存在",
    MessageError.error_param: "参数错误",
}

message_warn = {
    MessageWarn.package_release: "请确认是否打包release包并勾选必选项",
    MessageWarn.check_running: "敏感词扫描中...",
}


# 消息弹窗
class NotificationIcon:
    Info, Success, Warning, Error, Close = range(5)
    Types = {
        Info: None,
        Success: None,
        Warning: None,
        Error: None,
        Close: None
    }

    @classmethod
    def init(cls):
        cls.Types[cls.Info] = QPixmap(QImage.fromData(base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAC5ElEQVRYR8VX0VHbQBB9e/bkN3QQU0FMBSEVYFcQ8xPBJLJ1FWAqOMcaxogfTAWQCiAVRKkgTgfmM4zRZu6QhGzL0p0nDPr17e7bt7tv14RX/uiV48MJgAon+8TiAMRtMFogaqUJxADPwRRzg67kl8+xbWJWANR40iPQSSFgtX/mGQkaDr56V3VAKgGos4s2JXwJoF3naMPvMS+SrpTHs032GwGkdF+DsFMVnJm/oyGGeHico0EjIjpYes+YMyVd6R/flfkpBWCCQ9zaZM2LZDfLMGXsZ5kdI/lYBmINgHHyyLd1mWdBbAFAM/GY7K2WYx1AeB4T6L1N9umbGxZ0qktATaEAdCps48D39oq/LwEw3U5CN92LfczJoewfT7MAywDCaEbAuxeLrh0zz4L+0e4aAJfGy+sP3IMxlH1vpMJoSMCJDXgWtJeJVc6ACs9HBBrYODCJAFdYvAmkPJxnNqMwYht7Bn+T/lGg3z4DGEd3RPhQ54DBvwAOVkeqagRXfTLjh+x7+8sALOtfHLuiYzWOAiLoKbD58mnIGbCmLxUepS6NQmYlUGE0JeCTTXT9JvA9E9sZgO5iIpoyc6/YzcqSwQzgGgBXB7oXpH9klpRSkxY1xW/b7Iu2zk34PILPnazCqEPAtTWA8iZ0HsOu9L0bw4DzCJeNocMGNDpQ3IKO+6NUiJ4ysZNiBv5I3zPnmJmG5oM+wbS+9+qkvGi7NAXGmeUy0ioofa+XA0jH0UaMKpdRWs/adcwMqfV/tenqpqHY/Znt+j2gJi00RUzA201dXaxh9iZdZloJS+9H1otrkbRrD5InFqpPskxEshJQ468CkSmJC+i1HigaaxCAuCljgoDhwPdOjf7rFVxxuJrMkXScjtKc1rOLNpJk6nii5XmYzbngzlZn+RIb40kPJPTBYXUt6VEDJ8Pi6bWpNFb/jFYY6YGpDeKdjBmTKdMcxDGEmP73v2a2Gr/NOycGtglQZ/MPzEqCMLGckJEAAAAASUVORK5CYII=')))
        cls.Types[cls.Success] = QPixmap(QImage.fromData(base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACZUlEQVRYR8VXS3LTQBDtVsDbcAPMCbB3limkcAKSG4QFdnaYE2BOQLKzxSLJCeAGSUQheSnfwLmB2VJhXmpExpFHI2sk2RWv5FJPv9evP9NieuIfPzE+VSJw8qt3IMDvmahDoDYxt2UAACXMWIIowR5ffn8TJbaBWRE4CXvHAH9RgKXOgQUI48CfXZbZbiTw8Xe/w3d0zkydMkem91IZpyWOJu5sUXS+kEAqt3B+MNOLOuDqDEBLxxFHk7eza5MfIwEJDjhXTYD1s8zinYlEjsCD7FdNI9cJpEq0RFdPR47AMOzLCn69zegz6UgCP+pmfa8RSKudnPNdgCufTOLDxJtdPP7PoA1Cd8HEL5sSUCCD0B0x8bc1f8Bi6sevcgS2VXh6hMOwDz0gsUddNaxWKRjeuKfE/KlJ9Dq4UYH/o/Ns6scj+bgiMAjdayb26xLQwTfVEwg3gRcf6ARq578KuLo7VDc8psCQqwfjr4EfjYvkrAquFJ56UYpdSkAZSmNd1rrg0leOQFELgvA58OJTxVyRaAJORPOpF6UXnFUR5sDiXjs7UqsOMGMRlrWhTkJXpFL3mNrQZhA1lH3F0TiI5FurUQyMpn58VjhkSqQA4Tbw4nSVW6sBU5VXktXSeONlJH3s8jrOVr9RgVSFuNcWfzlh5n3LoKzMAPxxWuiULiQpiR2sZNnCyzIuWUr5Z1Ml0sgdHFZaShVDuR86/0huL3VXtDk/F4e11vKsTHLSCeKx7bYkW80hjLOrV1GhWH0ZrSlyh2MwdZhYfi8oZeYgLBmUiGd8sfVPM6syr2lUSYGaGBuP3QN6rVUwYV/egwAAAABJRU5ErkJggg==')))
        cls.Types[cls.Warning] = QPixmap(QImage.fromData(base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACmElEQVRYR8VXTW7TUBD+xjYSXZFukOIsSE9AskNJJMoJmq4r7OYEwAkabhBOkB/Emt4gVIojdpgbpIumEitX6gKB7UHPkauXxLHfc4F6Z3l+vvnmm/fGhAd+6IHzQwvA9cfOITMfAdQAcx1EdVEAM/tEFADsWyaPn57MfdXClABcT1qnzHSWJiwMzrwgoF91vXGRbS6AH59ajd8hDYmoURQo67tgxoij42rv62KX/04Agu44xmciVMokT32YERgGjquvZ1+y4mQCWPUa0/sk3vQlwqssEFsAVrQbU4XKL/ai2+5PPK6waQ4AOsoDnDARh83NdmwBuJq0fQI9L6p+L7rd3+/5gbAToMPI+FbkIzRRc72mbLcGIFE7jGFRIPHddmZrvstJh1X8CHGv6sxHqe1GkPYCoGcqgcoCAPPCdr2DLQC6wqMoPEj7qdqCNKllxs30sLpjYDluDUDGG5XqhY2sal3w4PiD7c7fJnHShMtJR8zpy/8CALiwndnhBgD1/t+XAXkaZAaUVHwnHulg0W6BNEWlAQD8zna8gQB0Ne70iXCm2j55jCUAei1gxvuaO+uXAcDg7zXHSy640iKUAehOEDJFqDmGQkiPLO5Fv+KADXOqvCuIsrPGsIyQdHou22YeRMJgOdHTQTkAfGk7XrLKrWlAvOhcRgBfWiZ3RQti0zxXuUFXCXMuo0TRitfxugjbIxC5RYzI6s9kIGFh+KLOpiW22id5AUuI8IaisFG4kCQg/sFKJgtPLix3KWXGeRETRbQDuCFCV2spTYMm+2FEI1WBbYIRPTeiqFtqLZeDraaD+qrbkpgQAvfl1WsXU0p/RjIjYYhTkNFgcCVlRlRKoAAc+5aF0V//NVPoc2kTLQZKZ8lx/AMXBmMwuXUwOAAAAABJRU5ErkJggg==')))
        cls.Types[cls.Error] = QPixmap(QImage.fromData(base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACrklEQVRYR82XW27aQBSG/4PtiNhIpStouoImKwjZAV1B07coWCpZQcgK6kh2lLeSFZSsIOwgdAdkBaUSEBQDpxpjU9vM+EJR03nDzJz/mzm3GcIrD3plfZQCeD47O1ho2jERNRmoE9AQG2BgBGBAwIiZe5Zh3JPjiG+5oxCAEF5q2iWITnMtRhOYu5XF4mr/9naYtSYXYGLbHQCXhYVTEwlom657rVqvBOB2uz71/a+ldq1SYe6ahnEhc4sSYGzbfQKOt915eh0D/ZrrnqS/SwEmrVYXRJ92Jb4OC+C65rrtuN0NgIltNwF837V4zN5Hy3V70e9NgFZrCKJ3CQDmJ9MwDsW36XzeB/AhA/CHqeuN2WxWX2paX2JraHneeynA+Pz8lCqVbxLjV5brimxAEJxqiEA8CjZVBvFy+bl2c9MV9hInoAw85qFpGEeRYQVEQjzMokcQHWxsiPne8jzh6j8AodGfyqNlHpiGcaKAkIk/gChwm2yYuv5W2FqfwLNtN5bAQ2bwySB83zENo50A8/1McaFRAU72XVek+mpk+D/JlIKI/xkee654uCbIhjVAqZIrgSgpLhiCwN4OAEj4vEB2yDybBCjsAol4ZD0nRdMQSRcUCsKUeNSw4o2mKMRGEOamoVx8FXDZKVosDYNMUHXAsBRnppo8RQcbpTgIGEkhykpFjnWxzGhPQYxt2yHgS/oIlKVYTJxImpG482nz+VG1Wh1N84pMCCGa0ULXHwmoJwCYnyzPW5fn/68dh7EgPbrMMl3gz7gro+n/7EoWD7w4a96l1NnJ1Yz5Lt6wCgFEk0r1CIkbiPnC9DxH5aHcd4FYGD5MOqVOg/muslh0/vphkm63k5eXZvA0I6qD+ZCI3jDzLxANiHn1NNvb6+30aVYgwLeeUsgFW1svsPA3Ncq4MHzVeO8AAAAASUVORK5CYII=')))
        cls.Types[cls.Close] = QPixmap(QImage.fromData(base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAeElEQVQ4T2NkoBAwUqifgboGzJy76AIjE3NCWmL0BWwumzV/qcH/f38XpCfHGcDkUVwAUsDw9+8GBmbmAHRDcMlheAGbQnwGYw0DZA1gp+JwFUgKZyDCDQGpwuIlrGGAHHAUGUCRFygKRIqjkeKERE6+oG5eIMcFAOqSchGwiKKAAAAAAElFTkSuQmCC')))

    @classmethod
    def icon(cls, ntype):
        return cls.Types.get(ntype)


class NotificationItem(QWidget):
    closed = pyqtSignal(QListWidgetItem)

    def __init__(self, title, message, item, *args, ntype=0, callback=None, **kwargs):
        super(NotificationItem, self).__init__(*args, **kwargs)
        self.item = item
        self.callback = callback
        layout = QHBoxLayout(self, spacing=0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.bgWidget = QWidget(self)  # 背景控件, 用于支持动画效果
        layout.addWidget(self.bgWidget)

        layout = QGridLayout(self.bgWidget)
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(10)

        # 标题左边图标
        layout.addWidget(
            QLabel(self, pixmap=NotificationIcon.icon(ntype)), 0, 0)

        # 标题
        self.labelTitle = QLabel(title, self)
        font = self.labelTitle.font()
        font.setBold(True)
        font.setPixelSize(22)
        self.labelTitle.setFont(font)

        # 关闭按钮
        self.labelClose = QLabel(
            self, cursor=Qt.PointingHandCursor, pixmap=NotificationIcon.icon(NotificationIcon.Close))

        # 消息内容
        self.labelMessage = QLabel(
            message, self, cursor=Qt.PointingHandCursor, wordWrap=True, alignment=Qt.AlignLeft | Qt.AlignTop)
        font = self.labelMessage.font()
        font.setPixelSize(20)
        self.labelMessage.setFont(font)
        self.labelMessage.adjustSize()

        # 添加到布局
        layout.addWidget(self.labelTitle, 0, 1)
        layout.addItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 2)
        layout.addWidget(self.labelClose, 0, 3)
        layout.addWidget(self.labelMessage, 1, 1, 1, 2)

        # 边框阴影
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(12)
        effect.setColor(QColor(0, 0, 0, 25))
        effect.setOffset(0, 2)
        self.setGraphicsEffect(effect)

        self.adjustSize()

        # 5秒自动关闭
        self._timer = QTimer(self, timeout=self.doClose)
        self._timer.setSingleShot(True)  # 只触发一次
        self._timer.start(3000)

    def doClose(self):
        try:
            # 可能由于手动点击导致item已经被删除了
            self.closed.emit(self.item)
        except:
            pass

    def showAnimation(self, width):
        # 显示动画
        pass

    def closeAnimation(self):
        # 关闭动画
        pass

    def mousePressEvent(self, event):
        super(NotificationItem, self).mousePressEvent(event)
        w = self.childAt(event.pos())
        if not w:
            return
        if w == self.labelClose:  # 点击关闭图标
            # 先尝试停止计时器
            self._timer.stop()
            self.closed.emit(self.item)
        elif w == self.labelMessage and self.callback and callable(self.callback):
            # 点击消息内容
            self._timer.stop()
            self.closed.emit(self.item)
            self.callback()  # 回调

    def paintEvent(self, event):
        # 圆角以及背景色
        super(NotificationItem, self).paintEvent(event)
        painter = QPainter(self)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 6, 6)
        painter.fillPath(path, Qt.white)


class NotificationWindow(QListWidget):
    _instance = None

    def __init__(self, *args, **kwargs):
        super(NotificationWindow, self).__init__(*args, **kwargs)
        self.setSpacing(20)
        self.setMinimumWidth(412)
        self.setMaximumWidth(412)
        QApplication.instance().setQuitOnLastWindowClosed(True)
        # 隐藏任务栏,无边框,置顶等
        self.setWindowFlags(self.windowFlags() | Qt.Tool |
                            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 去掉窗口边框
        self.setFrameShape(self.NoFrame)
        # 背景透明
        self.viewport().setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 不显示滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 获取屏幕高宽
        rect = QApplication.instance().desktop().availableGeometry(self)
        self.setMinimumHeight(rect.height())
        self.setMaximumHeight(rect.height())
        self.move(rect.width() - self.minimumWidth() - 18, 0)

    def removeItem(self, item):
        # 删除item
        w = self.itemWidget(item)
        self.removeItemWidget(item)
        item = self.takeItem(self.indexFromItem(item).row())
        w.close()
        w.deleteLater()
        del item

    @classmethod
    def _createInstance(cls):
        # 创建实例
        if not cls._instance:
            cls._instance = NotificationWindow()
            cls._instance.show()
            NotificationIcon.init()

    @classmethod
    def info(cls, title, message, callback=None):
        cls._createInstance()
        item = QListWidgetItem(cls._instance)
        w = NotificationItem(title, message, item, cls._instance,
                             ntype=NotificationIcon.Info, callback=callback)
        w.closed.connect(cls._instance.removeItem)
        item.setSizeHint(QSize(cls._instance.width() -
                               cls._instance.spacing(), w.height()))
        cls._instance.setItemWidget(item, w)

    @classmethod
    def success(cls, title, message, callback=None):
        cls._createInstance()
        item = QListWidgetItem(cls._instance)
        w = NotificationItem(title, message, item, cls._instance,
                             ntype=NotificationIcon.Success, callback=callback)
        w.closed.connect(cls._instance.removeItem)
        item.setSizeHint(QSize(cls._instance.width() -
                               cls._instance.spacing(), w.height()))
        cls._instance.setItemWidget(item, w)

    @classmethod
    def warning(cls, title, message, callback=None):
        cls._createInstance()
        item = QListWidgetItem(cls._instance)
        w = NotificationItem(title, message, item, cls._instance,
                             ntype=NotificationIcon.Warning, callback=callback)
        w.closed.connect(cls._instance.removeItem)
        item.setSizeHint(QSize(cls._instance.width() -
                               cls._instance.spacing(), w.height()))
        cls._instance.setItemWidget(item, w)

    @classmethod
    def error(cls, title, message, callback=None):
        cls._createInstance()
        item = QListWidgetItem(cls._instance)
        w = NotificationItem(title, message, item,
                             ntype=NotificationIcon.Error, callback=callback)
        w.closed.connect(cls._instance.removeItem)
        width = cls._instance.width() - cls._instance.spacing()
        item.setSizeHint(QSize(width, w.height()))
        cls._instance.setItemWidget(item, w)


# 基础dialog
class BaseDialog(QDialog):

    def __init__(self, width, height, name=""):
        super(BaseDialog, self).__init__()
        self.name = name
        self.width = width
        self.height = height
        self.__init_UI()

    def __init_UI(self):
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


# Box基类
class BaseBox(QGroupBox):
    common_signal = pyqtSignal(IntEnum, str, dict)

    def __init__(self, parent, name):
        super(BaseBox, self).__init__()
        self.parent = parent
        self.name = name
        self.data = {}
        self.path = ""

    def getName(self):
        return self.name

    def getData(self):
        return self.data

    def setData(self, data):
        self.data = data

    def setPath(self, path):
        self.path = path

    def getPath(self):
        return self.path

    def updateInfo(self):
        return


class dSYMCrashBox(QGroupBox, Ui_crashBox):

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.initUI()

    def initUI(self):
        self.setTitle(crash_titles[CrashBoxEnum.dSYM])

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().text().endswith(crash_suffix[CrashBoxEnum.dSYM]):
            print("dSYMCrashBox: dragEnterEvent")
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        src_file = event.mimeData().text().replace("file:///", "")
        if os.path.exists(src_file):
            dSYM_file = TEMP_PATH + "/AAA.dSYM"
            shutil.copyfile(src_file, dSYM_file)


class IpsBox(QGroupBox, Ui_ipsBox):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.setTitle(crash_titles[CrashBoxEnum.ips])

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().text().endswith(crash_suffix[CrashBoxEnum.ips]):
            print("ipsCrashBox: dragEnterEvent")
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        src_file = event.mimeData().text().replace("file:///", "")
        if os.path.exists(src_file):
            crash_file = TEMP_PATH + "/AAA.crash"
            shutil.copyfile(src_file, crash_file)


# 密钥生成框
class KeyRandomBox(QGroupBox, Ui_keyRandomBox):
    random_string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,.\/@*{}[]:'

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__init_UI()
        self.__init_data()

    def __init_UI(self):
        self.btn_check.clicked.connect(self.__action_event_key_random)
        self.lineEdit.setValidator(QIntValidator(1, 65535))
        self.lineEdit_2.setValidator(QIntValidator(1, 65535))
        self.lineEdit_3.setValidator(QRegExpValidator(QRegExp("^[a-zA-Z0-9]+$")))

    def __init_data(self):
        self.result = ""

    def __output_result(self, message):
        self.result = self.result + message + "\n"
        self.label.setText(self.result)

    def __random_key(self, mark, letters, numbers):
        try:
            passkey = []
            data = []
            for i in range(numbers):
                data.append(''.join(sample(self.random_string, letters)))
                passkey.append(mark.join(data))
                data = []
            return passkey
        except Exception as e:
            LOG.error(e)

    def __action_event_key_random(self):
        numbers = self.lineEdit.text()
        mark = self.lineEdit_3.text()
        letters = self.lineEdit_2.text()
        if not numbers or not mark or not letters:
            NotificationWindow.error(ERROR_TITLE, message_error[MessageError.error_param])
            return
        self.result = ""
        keys = self.__random_key(mark, int(letters), int(numbers))
        for key in keys:
            self.__output_result(key)


# 资源加密检测框
class ResCheckBox(QGroupBox, Ui_resCheckBox):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__init_UI()
        self.__init_data()

    def __init_UI(self):
        self.pushButton.clicked.connect(self.__action_event_select_res)
        self.btn_check.clicked.connect(self.__action_event_check_start)

    def __init_data(self):
        self.path = None
        self.is_running = False
        self.result = ""
        self.HEAD = None

    def __output_result(self, message):
        self.result = self.result + message + "\n"
        self.label.setText(self.result)

    def __check_res(self, key):
        result = []
        for root, dirs, files in os.walk(self.path):
            for filename in files:
                if os.path.splitext(filename)[1].lower() != '.mp3':
                    path = os.path.join(root, filename)
                    with open(path, 'rb') as f:
                        head = f.read(10)
                        if key.encode() != head:
                            result.append(path)
                            self.__output_result(f"没有加密的文件:{path}")
        return result

    def __check_thread(self, key):
        self.__output_result("扫描开始...")
        files = self.__check_res(key)
        if len(files) < 1:
            self.__output_result("扫描结束，一切正常")
        else:
            self.__output_result("扫描结束...")
        self.is_running = False

    def __action_event_select_res(self):
        path = QFileDialog.getExistingDirectory(self, "选取项目文件夹", self.path or sys.path[0])
        LOG.info(f"{self.path =}")
        if path:
            self.path = path
            self.textEdit.setPlainText(path)

    def __action_event_check_start(self):
        if not self.path:
            NotificationWindow.error(ERROR_TITLE, message_error[MessageError.not_exist_path])
            return
        key = self.textEdit_2.toPlainText()
        LOG.info(f"{key =}")
        if not key or key== "" or len(key) != 10:
            NotificationWindow.error(ERROR_TITLE, message_error[MessageError.no_key])
            return
        if self.is_running:
            NotificationWindow.warning(WARN_TITLE, message_warn[MessageWarn.check_running])
            return
        self.is_running = True
        self.result = ""
        self.sub_thread = threading.Thread(target=self.__check_thread, name="sub_thread", args=(key,))
        self.sub_thread.start()


# 代码检测框
class CodeCheckBox(QGroupBox, Ui_codeCheckBox):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__init_UI()
        self.__init_data()

    def __init_UI(self):
        self.pushButton.clicked.connect(self.__action_event_select_src)
        self.btn_check.clicked.connect(self.__action_event_check_start)

    def __init_data(self):
        self.path = None
        self.is_running = False
        self.result = ""

    def __output_result(self, message):
        self.result = self.result + message + "\n"
        self.label.setText(self.result)

    def __check_src(self):
        result = []
        for root, dirs, files in os.walk(self.path.replace("\\", "/")):
            for filename in files:
                filepath = os.path.join(root, filename)
                for target_str in CODE_CHECK_WORDS:
                    if filepath.find(target_str) >= 0:
                        result.append(filename)
                        self.__output_result(f"包含敏感词的文件:{filepath} | 铭感词:{target_str}")
                    if os.path.splitext(filename)[1] in ['.lua', '.txt', '.xml']:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if content.find(target_str) >= 0:
                                result.append(filename)
                                self.__output_result(f"包含敏感词的文件:{filename} | 铭感词:{target_str}")
        return result

    def __check_thread(self):
        self.__output_result("扫描开始...")
        files = self.__check_src()
        if len(files) < 1:
            self.__output_result("扫描结束，一切正常")
        else:
            self.__output_result("扫描结束...")
        self.is_running = False

    def __action_event_select_src(self):
        path = QFileDialog.getExistingDirectory(self, "选取项目文件夹", self.path or sys.path[0])
        LOG.info(f"{path =}")
        if path:
            self.path = path
            self.textEdit.setPlainText(path)

    def __action_event_check_start(self):
        if not self.path:
            NotificationWindow.error(ERROR_TITLE, message_error[MessageError.not_exist_path])
            return
        if self.is_running:
            NotificationWindow.warning(WARN_TITLE, message_warn[MessageWarn.check_running])
            return
        self.is_running = True
        self.result = ""
        self.sub_thread = threading.Thread(target=self.__check_thread, name="sub_thread")
        self.sub_thread.start()


# 敏感词检测框
class PackageCheckBox(QGroupBox, Ui_packageCheckBox):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__init_UI()
        self.__init_data()

    def __init_UI(self):
        self.pushButton.clicked.connect(self.__action_event_select_package)
        self.btn_check.clicked.connect(self.__action_event_check_start)

    def __init_data(self):
        self.path = None
        self.is_bundle = False
        self.is_running = False
        self.result = ""

    def __output_result(self, message):
        self.result = self.result + message + "\n"
        self.label.setText(self.result)

    def __check_file(self, Parser):
        result = []
        parser = Parser(filedir=self.path)
        for filename in parser.zfile.namelist():
            for target_str in PACKAGE_CHECK_WORDS:
                if filename.find(target_str) >= 0:
                    result.append(filename)
                    self.__output_result(f"包含敏感词的文件:{filename} 字段:{target_str}")
                if os.path.splitext(filename)[1] != '.dex':
                    with parser.zfile.open(filename) as f:
                        content = f.read()
                        if content.find(target_str.encode()) >= 0:
                            result.append(filename)
                            self.__output_result(f"包含敏感词的文件:{filename} 字段:{target_str}")
        assert parser.is_multidex is True
        for dex_filename in parser.get_all_dex_filenames():
            dex_obj = parser.get_dex(dex_filename)
            string_list = dex_obj.get_strings()
            for string_item in string_list:
                for target_str in PACKAGE_CHECK_WORDS:
                    if str(string_item).find(target_str) >= 0:
                        result.append(string_item)
                        self.__output_result(f"包含敏感词的dex:{dex_filename} 字段:{string_item}")
        return result

    def __check_thread(self):
        self.__output_result("扫描开始...")
        parser = AABParser if self.is_bundle else APKParser
        files = self.__check_file(parser)
        if len(files) < 1:
            self.__output_result("扫描结束，一切正常")
        else:
            self.__output_result("扫描结束...")
        self.is_running = False

    def __action_event_select_package(self):
        filepath, filetype = QFileDialog.getOpenFileName(self, '打开文件', "", 'APK (*.apk);;AAB (*.aab)')
        LOG.info(f"{filepath =} {self.is_bundle =}")
        if filepath:
            self.path = filepath
            self.textEdit.setPlainText(filepath)
            self.is_bundle = (filetype and filetype.find('APK') != 0)

    def __action_event_check_start(self):
        if not self.path:
            NotificationWindow.error(ERROR_TITLE, message_error[MessageError.not_exist_path])
            return
        if self.is_running:
            NotificationWindow.warning(WARN_TITLE, message_warn[MessageWarn.check_running])
            return
        self.is_running = True
        self.result = ""
        self.sub_thread = threading.Thread(target=self.__check_thread, name="sub_thread")
        self.sub_thread.start()


# 崩溃解析框
class CrashParseBox(QGroupBox, Ui_crashBox):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__init_UI()

    def __init_UI(self):
        print("initUI")


# ipa打包框
class IpaBox(QGroupBox, Ui_ipaBox):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.btn_select_ipa.clicked.connect(self.onClickedSelectPathIPA)
        self.btn_select_pod.clicked.connect(self.onClickedSelectPathPod)
        self.btn_ipa.clicked.connect(self.onClickedIPA)

    def onClickedSelectPathIPA(self):
        path = QFileDialog.getExistingDirectory(self, "选择ipa导出文件夹", self.path or sys.path[0])
        tmpPath = str(path)

        def endFunc():
            self.textEdit_ipa.setText(tmpPath)

        self.checkPathAndCallback(tmpPath, endFunc)

    def onClickedSelectPathPod(self):
        path = QFileDialog.getExistingDirectory(self, "选择pod存放文件夹", self.path or sys.path[0])
        tmpPath = str(path)

        def endFunc():
            self.textEdit_pod.setText(tmpPath)

        self.checkPathAndCallback(tmpPath, endFunc)

    def getIPAOutputPath(self):
        return self.textEdit_ipa.toPlainText()

    def onClickedIPA(self):
        output_path = self.getIPAOutputPath()

        def ipa():
            msg = "ipa"
            NotificationWindow.success(PROMPT_TITLE, msg, callback=lambda: LOG.info(msg))

        self.checkPathAndCallback(output_path, ipa)

    def checkPathAndCallback(self, path, callback):
        if path and path != "" and os.path.isdir(path):
            callback()
        else:
            NotificationWindow.error(ERROR_TITLE, message_error[MessageError.not_exist_path])


# 项目工具标签
class ToolsTab(QWidget, Ui_toolsForm):

    box_clz = {
        ToolsItemEnum.packageCheck: PackageCheckBox,
        ToolsItemEnum.codeCheck: CodeCheckBox,
        ToolsItemEnum.resCheck: ResCheckBox,
        ToolsItemEnum.keyRandom: KeyRandomBox,
        ToolsItemEnum.ipa: IpaBox,
        ToolsItemEnum.ips: CrashParseBox,
    }

    def __init__(self):
        super(ToolsTab, self).__init__()
        self.setupUi(self)
        self.__init_UI()

    def __init_UI(self):
        itemEnum = ToolsItemEnum(1)
        for name in tools_item_titles.values():
            # item
            item = ListItem(name)
            item.setSizeHint(QSize(ITEM_WIDTH, ITEM_HEIGHT))
            self.listWidget.addItem(item)
            # box
            box = self.box_clz[itemEnum]()
            self.stackedWidget.addWidget(box)
            itemEnum += 1
        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)
        self.listWidget.setCurrentRow(0)


# 关于对话框
class AboutDialog(QDialog, Ui_aboutDialog):

    def __init__(self):
        super(AboutDialog, self).__init__()
        self.setupUi(self)


# 工具集
class MogooTools(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MogooTools, self).__init__()
        self.setupUi(self)
        self.__log_infomation_base()
        self.__init_UI()

    def __log_infomation_base(self):
        LOG.info("------------------------------------")
        LOG.info("用户目录:{0}".format(USER_PATH))
        LOG.info("工作目录:{0}".format(WORK_PATH))
        LOG.info("工作模式:{0}".format("debug" if IS_DEBUG_MODE else "release"))
        LOG.info("操作系统:{0}".format(sys.platform))
        LOG.info("------------------------------------")

    def __init_UI(self):
        self.openConfigAction.triggered.connect(self.__action_event_open_config)
        self.action_about.triggered.connect(self.__action_event_show_about)
        self.tabWidget.addTab(ToolsTab(), "默认")
        self.resize(UI_WIDTH, UI_HEIGHT)
        frame = self.frameGeometry()
        frame.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())
        self.setWindowTitle(UI_TITLE)
        LOG.info("初始化UI成功")

    def __action_event_open_config(self):
        OpenDir(WORK_PATH)

    def __action_event_show_about(self):
        dialog = AboutDialog()
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    def closeWin(self):
        self.close()

    def destroy(self, **kwargs):
        self.close()

    def closeEvent(self, event):
        if IS_DEBUG_MODE:
            self.destroy()
        else:
            self.__close_UI(lambda: event.ignore())

    def __close_UI(self, onerror):
        ret = QMessageBox.question(self, '消息框', "确定关闭程序？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.destroy()
        elif onerror:
            onerror()


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./icon/256.ico'))
    tools = MogooTools()
    tools.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
