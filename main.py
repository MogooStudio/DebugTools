import os.path
import plistlib
import sys
import re
# import plistlib
from biplist import *
from enum import IntEnum

from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QDialog, QGroupBox, QLabel, \
    QListWidgetItem, QTableWidgetItem, \
    QWidget, QApplication, QMainWindow, \
    QMessageBox, QDesktopWidget

from mainUI import Ui_MainWindow
from groupForm import Ui_groupForm
from debugBox import Ui_debugBox
from packageBox import Ui_packageBox
from uploadBox import Ui_uploadBox

from log import info
from model import Model

is_debug = True


class ItemEnum(IntEnum):
    debug = 1
    upload = 2
    ipa = 3


class ConfigEnum(IntEnum):
    pad = 1
    dialog = 2
    download = 3
    splunk = 4
    server = 5


class ServerUrlEnum(IntEnum):
    offline_test = 1
    online_test = 2
    online = 3


class PlatformEnum(IntEnum):
    android = 1
    ios = 2


ui_title = "调试工具"
ui_width = 1280
ui_height = 720

item_width = 150
item_height = 80
item_titles = {
    ItemEnum.debug: "调试配置",
    ItemEnum.upload: "上传资源",
    ItemEnum.ipa: "打包ipa",
}

tab_group_titles = ["game1", "game2", "game3"]

game_package_names = {
    "game1": ["googleAvidlyFirst", "ios_avidly"],
    "game2": ["googleHummer2Third", "ios_cashmania"],
    "game3": ["googleAvidly3First", "ios_vegasparty"],
}

debug_config_path = {
    "game1": "/src/",
    "game2": "/src/",
    "game3": "/src/framework/devMode/",
}

common_config_path = {
    "game1": "/src/",
    "game2": "/src/",
    "game3": "/src/framework/",
}

debug_key = {
    ConfigEnum.pad: "pad",
    ConfigEnum.dialog: "dialog",
    ConfigEnum.download: "download",
    ConfigEnum.splunk: "splunk",
    ConfigEnum.server: "server",
}

download_url = {
    "game1": "http://192.168.1.201/slots_assets/101/",
    "game2": "http://192.168.1.201/slots_assets/102/",
    "game3": "http://192.168.1.201/slots_assets/103/",
}

server_http_url = {
    ServerUrlEnum.online: "http://avd-game3-slots-elb-995507315.us-west-2.elb.amazonaws.com/api",
    ServerUrlEnum.offline_test: "http://192.168.1.201/hm-game3/www/game3/debug/api.php",
    ServerUrlEnum.online_test: "http://ec2-52-33-159-0.us-west-2.compute.amazonaws.com/api",
}

server_report_url = {
    ServerUrlEnum.online: "http://avd-game3-slots-elb-995507315.us-west-2.elb.amazonaws.com/report",
    ServerUrlEnum.offline_test: "http://192.168.1.201/hm-game3/www/game3/debug/report.php",
    ServerUrlEnum.online_test: "http://ec2-52-33-159-0.us-west-2.compute.amazonaws.com/report",
}

server_stat_url = {
    ServerUrlEnum.online: "http://avd-game3-slots-elb-995507315.us-west-2.elb.amazonaws.com/stat",
    ServerUrlEnum.offline_test: "http://192.168.1.201/hm-game3/www/game3/debug/stat.php",
    ServerUrlEnum.online_test: "http://ec2-52-33-159-0.us-west-2.compute.amazonaws.com/stat",
}

server_terms_url = {
    ServerUrlEnum.online: "http://avd-game3-slots-elb-995507315.us-west-2.elb.amazonaws.com/terms",
    ServerUrlEnum.offline_test: "http://192.168.1.201/hm-game3/www/game3/debug/terms.php",
    ServerUrlEnum.online_test: "http://ec2-52-33-159-0.us-west-2.compute.amazonaws.com/terms",
}

config_theme = """
-------------------------------------------------------------
---------------------------Theme1 数据写死  debug_num至少从11开始
-------------------------------------------------------------
G_ADJUST_SPIN_ITEM_LIST_FUNC = function( themeStatus, spinParam, spinReels )
    local a = G_THEME1_DEBUG_BY_FIX and G_THEME1_DEBUG_BY_FIX(themeStatus, spinParam, spinReels)
end
-------------------------------------------------------------
---------------------------Theme1 数据筛选
-------------------------------------------------------------
G_ADJUST_SPIN_RES_BY_FILTRATION = function( spinResult )
    local SUM_WIN       = spinResult[K_SPIN_STAT_DATA][K_STAT_SUM_WIN]
    local TOTAL_BET     = spinResult[K_SPIN_BASE_DATA][K_SPIN_TOTAL_BET]
    local NORMAL        = not spinResult[K_SPIN_STAT_DATA][K_STAT_FEATURE_DATA][K_STAT_FEATURE_TYPE.NORMAL]
    local FS_GAME       = not spinResult[K_SPIN_STAT_DATA][K_STAT_FEATURE_DATA][K_STAT_FEATURE_TYPE.FREE_SPIN_GAME]
    local FREE_SPIN     = not spinResult[K_SPIN_STAT_DATA][K_STAT_FEATURE_DATA][K_STAT_FEATURE_TYPE.FREE_SPIN]
    local RESPIN_NM     = not spinResult[K_SPIN_STAT_DATA][K_STAT_FEATURE_DATA][K_STAT_FEATURE_TYPE.NORMAL_RESPIN]
    local VEGAS         = not spinResult[K_SPIN_STAT_DATA][K_STAT_FEATURE_DATA][K_STAT_FEATURE_TYPE.VEGAS_BONUS]
    local LITTlE_WIN    = not (SUM_WIN / TOTAL_BET >= 5 and SUM_WIN / TOTAL_BET < 8)
    local BIG_WIN       = not (SUM_WIN / TOTAL_BET >= 8 and SUM_WIN / TOTAL_BET < 15)
    local MEGA_WIN      = not (SUM_WIN / TOTAL_BET >= 15 and SUM_WIN / TOTAL_BET < 25)
    local SUPER_WIN     = not (SUM_WIN / TOTAL_BET >= 25 and SUM_WIN / TOTAL_BET < 40)
    local EPIC_WIN      = not (SUM_WIN / TOTAL_BET >= 40 )
    ------------------------------------------------------------------------------------------------------
    -------------------恢复
    -------------------free spin 
    if DEBUG_NUM1 == 2 and FREE_SPIN then
        return true
    end
    -------------------free spin game
    if DEBUG_NUM1 == 3 and FS_GAME then
        return true
    end
    -------------------normal respin
    if DEBUG_NUM1 == 4 and RESPIN_NM then
        return true
    end
    -------------------vegas respin
    if DEBUG_NUM1 == 5 and VEGAS then
        return true
    end
    -------------------little win  5-8 mul
    if DEBUG_NUM1 == 6 and (LITTlE_WIN or not FREE_SPIN or not FS_GAME or not VEGAS) then
        return true
    end
    -------------------big win  8-15 mul
    if DEBUG_NUM1 == 7 and (BIG_WIN or not FREE_SPIN or not FS_GAME or not VEGAS) then
        return true
    end
    -------------------mega win  15-25 mul
    if DEBUG_NUM1 == 8 and (MEGA_WIN or not FREE_SPIN or not FS_GAME or not VEGAS) then
        return true
    end
    -------------------super win  25-40 mul
    if DEBUG_NUM1 == 9 and (SUPER_WIN or not FREE_SPIN or not FS_GAME or not VEGAS) then
        return true
    end
    -------------------epic win  40+ mul
    if DEBUG_NUM1 == 10 and (EPIC_WIN or not FREE_SPIN or not FS_GAME or not VEGAS) then
        return true
    end
    if G_THEME1_DEBUG_BY_FILTER then
        return G_THEME1_DEBUG_BY_FILTER(spinResult)
    end
    return false
end 

-------------------------------------------------------------
---------------------------Theme2 数据写死
-------------------------------------------------------------
DEBUG_GET_CHEAT_STOP_DATA = function()
    local result = G_THEME2_DEBUG_BY_FIX and G_THEME2_DEBUG_BY_FIX()
    return result
end
-------------------------------------------------------------
---------------------------Theme2 数据筛选
-------------------------------------------------------------
DEBUG_PANEL_CHEAT_FILTER = function(spinResult)
    --测试环境下且白名单用户
    if not appDebugMode and not Config.whiteTag then
        return nil
    end
    if not spinResult or next(spinResult) == nil then
        return false
    end
    local gameState = spinResult["gameState"]
    if not gameState then
        return false
    end
    if gameState ~= "base" then
        return false
    end
    local SUM_WIN       = spinResult["winAmount"]
    local TOTAL_BET     = spinResult["betData"] or spinResult["spinBaseData"]["total_bet"] 
    local FREE_SPIN     = not spinResult["freeGameData"] or not spinResult["freeGameData"]["is_active"]
    local FS_GAME       = not spinResult["jackpotGameData"]
    local VEGAS         = not (spinResult["featureGameData"] and spinResult["featureGameData"]["respin"] and spinResult["featureGameData"]["respin"]["is_active"])
    local JACKPOT       = not (spinResult["specialSymbolData"] and spinResult["specialSymbolData"]["r"] and spinResult["specialSymbolData"]["r"]["triggerID"])
    local LITTlE_WIN    = SUM_WIN / TOTAL_BET < 5 or SUM_WIN / TOTAL_BET > 8
    local BIG_WIN       = SUM_WIN / TOTAL_BET < 8   or SUM_WIN / TOTAL_BET > 15
    local MEGA_WIN      = SUM_WIN / TOTAL_BET < 15  or SUM_WIN / TOTAL_BET > 25
    local SUPER_WIN     = SUM_WIN / TOTAL_BET < 25  or SUM_WIN / TOTAL_BET > 40
    local EPIC_WIN      = SUM_WIN / TOTAL_BET < 40 
    -------------------什么都不中
    if DEBUG_NUM1 == 1 and not FREE_SPIN and not FS_GAME and not VEGAS then
        return true
    end
    -------------------free spin 
    if DEBUG_NUM1 == 2 and FREE_SPIN then
        return true
    end
    -------------------free spin game
    if DEBUG_NUM1 == 3 and FS_GAME then
        return true
    end
    -------------------normal respin
    if DEBUG_NUM1 == 4 and JACKPOT then
        return true
    end
    -------------------vegas respin
    if DEBUG_NUM1 == 5 and VEGAS then
        return true
    end
    -------------------little win  5-8 mul
    if DEBUG_NUM1 == 6 and LITTlE_WIN then
        return true
    end
    -------------------big win  8-15 mul
    if DEBUG_NUM1 == 7 and BIG_WIN then
        return true
    end
    -------------------mega win  15-25 mul
    if DEBUG_NUM1 == 8 and MEGA_WIN then
        return true
    end
    -------------------super win  25-40 mul
    if DEBUG_NUM1 == 9 and SUPER_WIN then
        return true
    end
    -------------------epic win  40+ mul
    if DEBUG_NUM1 == 10 and EPIC_WIN then
        return true
    end
    if G_THEME2_DEBUG_BY_FILTER then
        return G_THEME2_DEBUG_BY_FILTER(spinResult)
    end
    --############################################--
    return false
end
"""

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
    common_signal = pyqtSignal(str, dict)

    def __init__(self, parent, title):
        super(DebugBox, self).__init__()
        self.parent = parent
        self.title = title
        self.selectPad = False
        self.selectDialog = False
        self.selectDownload = False
        self.selectEnv = False
        self.selectSplunk = False
        self.indexServerPath = 0
        self.indexGamePackage = 0
        self.data = None
        self.path = ""
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        # mod btn
        self.btn_mod_game.clicked.connect(self.onClickedModBtn)
        # debug item
        self.no_pad.toggled.connect(self.onSelectedPadBtn)
        self.no_dialog.toggled.connect(self.onSelectedDialogBtn)
        self.no_download.toggled.connect(self.onSelectedDownloadBtn)
        self.no_splunk.toggled.connect(self.onSelectedSplunkBtn)
        self.box_server_path.insertItem(0, "--请选择--")
        self.box_server_path.currentIndexChanged.connect(self.onSelectedServerPath)
        game = self.parent.getGameGroup()
        packages = game_package_names[game]
        self.box_game_package.addItem("--请选择--")
        self.box_game_package.insertItem(PlatformEnum.android, packages[PlatformEnum.android - 1])
        self.box_game_package.insertItem(PlatformEnum.ios, packages[PlatformEnum.ios - 1])
        self.box_game_package.setCurrentIndex(0)
        self.box_game_package.currentIndexChanged.connect(self.onSelectedGamePackage)
        self.updateUI()

    def updateUI(self):
        self.no_pad.setChecked(not self.selectPad)
        self.yes_pad.setChecked(self.selectPad)
        self.no_dialog.setChecked(not self.selectDialog)
        self.yes_dialog.setChecked(self.selectDialog)
        self.no_download.setChecked(not self.selectDownload)
        self.yes_download.setChecked(self.selectDownload)
        self.no_splunk.setChecked(not self.selectSplunk)
        self.yes_splunk.setChecked(self.selectSplunk)
        self.box_server_path.setCurrentIndex(self.indexServerPath)
        self.box_game_package.setCurrentIndex(self.indexGamePackage)

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

    def onSelectedSplunkBtn(self):
        self.selectSplunk = self.yes_splunk.isChecked()
        if self.selectSplunk:
            info("打开强制打点")
        else:
            info("关闭强制打点")

    def onSelectedServerPath(self, index):
        self.indexServerPath = index
        if index == 1:
            info("内网测试服务器")
        elif index == 2:
            info("外网测试服务器")
        elif index == 3:
            info("线上正式服务器")

    def onSelectedGamePackage(self, index):
        self.indexGamePackage = index - 1
        self.updateGamePackageList()

    def onClickedModBtn(self):
        self.common_signal.emit(self.title, self.getData())

    def getData(self):
        return {
            debug_key[ConfigEnum.pad]: self.selectPad,
            debug_key[ConfigEnum.dialog]: self.selectDialog,
            debug_key[ConfigEnum.download]: self.selectDownload,
            debug_key[ConfigEnum.splunk]: self.selectSplunk,
            debug_key[ConfigEnum.server]: self.indexServerPath,
        }

    def getCdn(self, properties):
        gameCdn = []
        resCdn = []
        if os.path.isfile(properties):
            count = 1
            with open(properties, 'r') as f:
                for line in f.readlines():
                    if count == 1:
                        items = line.split('=')[1].replace("\n","")
                        gameCdn = items.split(':')
                    if count == 2:
                        items = line.split('=')[1].replace("\n","")
                        resCdn = items.split(':')
                    count += 1
        return gameCdn, resCdn

    def updateGamePackageList(self):
        print("updateGamePackageList")
        path = self.path
        game = self.parent.getGameGroup()
        packages = game_package_names[game]
        package_config = path + "/res_game/config/" + packages[self.indexGamePackage] + "/config.properties"
        print(package_config)
        gameCdn, resCdn = self.getCdn(package_config)
        for game in gameCdn:
            print(game)
        for res in resCdn:
            print(res)


    def setVersionInfo(self):
        path = self.path
        game = self.parent.getGameGroup()
        # git version android
        config_plist = path + common_config_path[game] + "config.plist"
        with open(config_plist, "rb") as fp:
            pl = plistlib.load(fp)
            self.lab_git_android.setText(pl["gitVersion"])
        # code version android
        config_platform = path + "/res_game/config/googleAvidly3First/platformConfig.lua"
        with open(config_platform, "r") as fp:
            content = fp.read()
            match_obj = re.search(r"Config\.version\s*=\s*\"(\d*\.\d*)\"", content)
            self.lab_code_android.setText(match_obj.group(1))
        # git&code version ios
        config_platform = path + "/res_game/config/ios_vegasparty/platformConfig.lua"
        with open(config_platform, "r") as fp:
            content = fp.read()
            match_obj = re.search(r"Config\.gitVersion\s*=\s*\"([^\"]*)\"", content)
            self.lab_git_ios.setText(match_obj.group(1))
            match_obj = re.search(r"Config\.version\s*=\s*\"(\d*\.\d*)\"", content)
            self.lab_code_ios.setText(match_obj.group(1))

    # def setGamePackage(self):
        # path = self.path
        # game = self.parent.getGameGroup()
        # packages = game_package_names[game]
        # self.box_game_package.insertItem(PlatformEnum.android, packages[PlatformEnum.android-1])
        # self.box_game_package.insertItem(PlatformEnum.ios, packages[PlatformEnum.ios-1])
        # self.box_game_package.setCurrentIndex(0)


    def setData(self, data):
        self.data = data
        print("setData: ", data)
        self.path = data["path"]
        self.setVersionInfo()
        # self.setGamePackage()
        debug = data[self.title]
        key = debug_key[ConfigEnum.pad]
        self.selectPad = debug[key]
        key = debug_key[ConfigEnum.dialog]
        self.selectDialog = debug[key]
        key = debug_key[ConfigEnum.download]
        self.selectDownload = debug[key]
        key = debug_key[ConfigEnum.splunk]
        self.selectSplunk = debug[key]
        key = debug_key[ConfigEnum.server]
        self.indexServerPath = debug[key]
        self.updateUI()


# 上传资源
class UploadBox(QGroupBox, Ui_uploadBox):
    common_signal = pyqtSignal(dict)

    def __init__(self, parent, title):
        super(UploadBox, self).__init__()
        self.parent = parent
        self.title = title
        self.setupUi(self)

    def getData(self):
        return {}

    def setData(self, data):
        print(data)


# 打包ipa框
class PackageBox(QGroupBox, Ui_packageBox):
    common_signal = pyqtSignal(dict)

    def __init__(self, parent, title):
        super(PackageBox, self).__init__()
        self.parent = parent
        self.title = title
        self.setupUi(self)

    def getData(self):
        return {}

    def setData(self, data):
        print(data)


# game选择tab
class TabGroupView(QWidget, Ui_groupForm):
    common_signal = pyqtSignal(str)

    box_clz = {
        ItemEnum.debug: DebugBox,
        ItemEnum.ipa: PackageBox,
        ItemEnum.upload: UploadBox,
    }

    def __init__(self, game):
        super(TabGroupView, self).__init__()
        self.game = game
        self.box_handle = {
            ItemEnum.debug: self.handleDebug,
            ItemEnum.ipa: self.handleIPA,
            ItemEnum.upload: self.handleUpload,
        }
        self.boxs = []
        self.model = Model(self.game)
        self.setupUi(self)
        self.initUI()
        self.initData()

    def initData(self):
        data = self.model.load()
        if not data:
            return
        self.setProjectPath(data['path'])
        for box in self.boxs:
            box.setData(data)

    def initUI(self):
        itemEnum = ItemEnum(1)
        for title in item_titles.values():
            item = ListItem(title)
            item.setSizeHint(QSize(item_width, item_height))
            self.listWidget.addItem(item)

            box = self.box_clz[itemEnum](self, title)
            box.common_signal.connect(self.box_handle[itemEnum])
            self.boxs.append(box)
            self.stackedWidget.addWidget(box)

            itemEnum += 1

        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)
        self.listWidget.setCurrentRow(0)

        self.btn_setting.clicked.connect(self.buttonClicked)

    def buttonClicked(self):
        get_directory_path = QFileDialog.getExistingDirectory(self, "选取指定文件夹", sys.path[0])
        self.textEdit_path.setText(str(get_directory_path))

    def setProjectPath(self, path):
        text = path if path and path != "" else ""
        self.textEdit_path.setText(text)

    def getProjectPath(self):
        return self.textEdit_path.toPlainText()

    def checkProjectPath(self, path):
        res_dir = path + "/res"
        src_dir = path + "/src"
        if path and path != "" and os.path.exists(res_dir) and os.path.exists(src_dir):
            return True

    def handleDebug(self, title, data):
        path = self.getProjectPath()
        if not self.checkProjectPath(path):
            return QMessageBox.critical(self, "错误", "项目路径不正确", QMessageBox.Ok)
        self.model.save({title: data, "game": self.game, "path": path})
        print("保存调试配置: ", title, data, self.game, path)

        key = debug_key[ConfigEnum.pad]
        pad = "" if data[key] else "--"
        key = debug_key[ConfigEnum.dialog]
        dialog = "" if data[key] else "--"
        key = debug_key[ConfigEnum.download]
        download = "--" if data[key] else ""
        key = debug_key[ConfigEnum.splunk]
        splunk = "" if data[key] else "--"
        key = debug_key[ConfigEnum.server]
        server = ServerUrlEnum(data[key])
        http_url = server_http_url[server]
        report_url = server_report_url[server]
        stat_url = server_stat_url[server]
        terms_url = server_terms_url[server]

        config_lua = path + debug_config_path[self.game] + "selfConfig.lua"
        with open(config_lua, 'w') as fp:
            fp.write("Native_path =\n")
            fp.write("{\n")
            fp.write("\tsearchPath = {},\n")
            fp.write("\thotUpdateSwitchOff = true,\n")
            fp.write("\tdbUseFileTag = true,\n")
            fp.write("\tthemeDevelopIdList = {},\n")
            fp.write("\t{0}server = \"{1}\"\n".format(download, download_url[self.game]))
            fp.write("}\n")
            fp.write("{0}Config.blockWindow = true\n".format(dialog))
            fp.write("--Config.checkActivityRes = true\n")
            fp.write("{0}hummer.padTag = true\n".format(pad))
            fp.write("{0}Config.forceOpenSplunkLog = true\n".format(splunk))
            fp.write("Config.httpServer = \"{0}\"\n".format(http_url))
            fp.write("Config.reportURL = \"{0}\"\n".format(report_url))
            fp.write("Config.statURL = \"{0}\"\n".format(stat_url))
            fp.write("Config.termsOfServiceURL = \"{0}\"\n".format(terms_url))
            fp.write(config_theme)

    def handleIPA(self, title, data):
        print("打包ipa")

    def handleUpload(self, title, data):
        print("上传资源")

    def getGameGroup(self):
        return self.game


class DebugTools(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(DebugTools, self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        for title in tab_group_titles:
            self.tabWidget.addTab(TabGroupView(title), title)

        self.resize(ui_width, ui_height)
        frame = self.frameGeometry()
        frame.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())
        self.setWindowTitle(ui_title)
        info("初始化UI")

    def setProjectRoot(self, path):
        info(path)

    def packageIPA(self):
        info("打包ipa")

    def uploadRes(self):
        info("上传资源")

    def closeWin(self):
        self.close()
        info("关闭窗口")

    def destroy(self):
        self.close()

    def closeEvent(self, event):
        if is_debug:
            self.destroy()
        else:
            self.closeUI(lambda: event.ignore())

    def closeUI(self, onerror):
        ret = QMessageBox.question(self, '消息框', "确定关闭程序？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
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
