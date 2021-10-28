import os
import sys
import re
import plistlib
import datetime
import subprocess
from enum import IntEnum

from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, QUrl, QStandardPaths, QObject
from PyQt5.QtWidgets import QFileDialog, QDialog, QGroupBox, QListWidgetItem, \
    QWidget, QApplication, QMainWindow, \
    QMessageBox, QDesktopWidget

from mainUI import Ui_MainWindow
from groupForm import Ui_groupForm
from debugBox import Ui_debugBox
from packageBox import Ui_packageBox
from hotupdateBox import Ui_hotupdateBox

from model import Model


# 全局函数
def WritFile(filename, content):
    with open(filename, "w") as fp:
        fp.write(content)


def ReadFile(filename):
    with open(filename, "r") as fp:
        return fp.read()


def ReadPlist(filename):
    with open(filename, "rb") as fp:
        return plistlib.load(fp)


def MakeDir(dirPath):
    if dirPath and not os.path.exists(dirPath):
        os.makedirs(dirPath)


def OpenDir(dirPath):
    if IS_MAC:
        os.system("open " + dirPath)
    else:
        QDesktopServices.openUrl(QUrl(dirPath))


# 全局变量
IS_DEBUG_MODE = True
IS_MAC = sys.platform == "darwin"
USER_PATH = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
WORK_PATH = USER_PATH + "/.debugtools"
MakeDir(WORK_PATH)


class ItemEnum(IntEnum):
    debug = 1
    ipa = 2


class ConfigEnum(IntEnum):
    pad = 1
    dialog = 2
    download = 3
    splunk = 4
    server = 5


class ServerUrlEnum(IntEnum):
    offline_test = 0
    online_test = 1
    online = 2


class PlatformEnum(IntEnum):
    android = 0
    ios = 1


class MessageError(IntEnum):
    project_path = 1
    config_lua = 2
    res_cdn_path = 3
    config_dir = 4
    not_exist_path = 5


class DebugBoxError(IntEnum):
    save = 1
    delete = 2
    open = 3


UI_TITLE = "调试工具"
UI_WIDTH = 1280
UI_HEIGHT = 900

ITEM_WIDTH = 150
ITEM_HEIGHT = 80
item_titles = {
    ItemEnum.debug: "调试配置",
    ItemEnum.ipa: "打包ipa",
}

ERROR_TITLE = "错误"

tab_group_titles = ["game1", "game2", "game3"]

game_package_names = {
    "game1": ["googleAvidlyFirst", "ios_avidly"],
    "game2": ["googleHummer2Third", "ios_cashmania"],
    "game3": ["googleAvidly3First", "ios_vegasparty"],
}

game_path_tag = {
    "game1": "101",
    "game2": "102",
    "game3": "103",
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

message_error = {
    MessageError.project_path: "路径不正确，请重新设置",
    MessageError.config_lua: "配置文件selfConfig不存在",
    MessageError.res_cdn_path: "路径不正确，请重新设置",
    MessageError.config_dir: "配置文件路径不正确",
    MessageError.not_exist_path: "路径不存在",

}

hotupdate_tag = {
    "game1": "runOnIosSimulator",
    "game2": "runOnIosSimulator",
    "game3": "hotUpdateSwitchOff",
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
---------------------------默认筛选配置
ALL_PASS = true
SELECT_TAG = 0
K_SPIN_MAX_FILTER_COUNT     = 2000

-------------------------------------------------------------
---------------------------Theme1 数据写死  debug_num至少从11开始
-------------------------------------------------------------
G_ADJUST_SPIN_ITEM_LIST_FUNC = function( themeStatus, spinParam, spinReels )
    if DEBUG_NUM1 == 11 then
        spinReels[K_SPIN_ITEM_LIST][1][1] = 1
        spinReels[K_SPIN_ITEM_LIST][1][2] = 1
        spinReels[K_SPIN_ITEM_LIST][1][3] = 1

        spinReels[K_SPIN_ITEM_LIST][2][1] = 1
        spinReels[K_SPIN_ITEM_LIST][2][2] = 1
        spinReels[K_SPIN_ITEM_LIST][2][3] = 1

        spinReels[K_SPIN_ITEM_LIST][3][1] = 1
        spinReels[K_SPIN_ITEM_LIST][3][2] = 1
        spinReels[K_SPIN_ITEM_LIST][3][3] = 1

        spinReels[K_SPIN_ITEM_LIST][4][1] = 1
        spinReels[K_SPIN_ITEM_LIST][4][2] = 1
        spinReels[K_SPIN_ITEM_LIST][4][3] = 1

        spinReels[K_SPIN_ITEM_LIST][5][1] = 1
        spinReels[K_SPIN_ITEM_LIST][5][2] = 1
        spinReels[K_SPIN_ITEM_LIST][5][3] = 1
    end
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
    if DEBUG_NUM1 == 0 then
        ALL_PASS = true
        SELECT_TAG = 0
    end
    -------------------什么都不中
    if DEBUG_NUM1 == 1 then
        ALL_PASS = false
        SELECT_TAG = 1
    end
    -------------------free spin 
    if DEBUG_NUM1 == 2 and FREE_SPIN then
        ALL_PASS = true
        SELECT_TAG = 2
        return true
    end
    -------------------free spin game
    if DEBUG_NUM1 == 3 and FS_GAME then
        ALL_PASS = true
        SELECT_TAG = 3
        return true
    end
    -------------------normal respin
    if DEBUG_NUM1 == 4 and RESPIN_NM then
        ALL_PASS = true
        SELECT_TAG = 4
        return true
    end
    -------------------vegas respin
    if DEBUG_NUM1 == 5 and VEGAS then
        ALL_PASS = true
        SELECT_TAG = 5
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
    return false
end 

-------------------------------------------------------------
---------------------------Theme2 数据写死
-------------------------------------------------------------
DEBUG_GET_CHEAT_STOP_DATA = function()
    --测试环境下且白名单用户
    if not appDebugMode and not Config.whiteTag then
        return nil
    end
    local cheat_data = {
        [1] = {
            {
                 [1] = {
                    {3,2,3},
                    {"s","g",4},
                    {"s",2,2},
                    {"s","g",6},
                    {2,2,1},
                },
            }
        },
    }
    if DEBUG_NUM1 and DEBUG_NUM1 == 11 then
        local result = cheat_data[1][1]
        return table.copy(result)
    end
    return nil
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
    local TOTAL_BET     = spinResult["betData"]
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
    return false
end
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


# Box基类
class BaseBox(QGroupBox):
    common_signal = pyqtSignal(IntEnum, str, dict)

    def __init__(self, parent, name):
        super(BaseBox, self).__init__()
        self.parent = parent
        self.name = name
        self.data = {}
        self.path = ""

    def getData(self):
        return self.data

    def setData(self, data):
        self.data = data.get(self.name) or self.data
        path = data.get("path") or self.path
        self.setPath(path)

    def setPath(self, path):
        self.path = path
        self.updateInfo()

    def getPath(self):
        return self.path

    def initInfo(self):
        print()

    def resetInfo(self):
        print()

    def updateInfo(self):
        print()


# 调试项目框
class DebugBox(BaseBox, Ui_debugBox):

    def __init__(self, parent, name):
        super(DebugBox, self).__init__(parent, name)
        self.gameCdn = []
        self.resCdn = []
        self.msgTimer = QTimer()
        self.setupUi(self)
        self.initInfo()
        self.initUI()
        self.updateUI()

    def initUI(self):
        self.btn_change_config.clicked.connect(self.onClickedChangeConfig)
        self.btn_reset_config.clicked.connect(self.onClickedResetConfig)
        self.btn_del_config.clicked.connect(self.onClickedDeleteConfig)
        self.btn_open_config.clicked.connect(self.onClickedOpenConfigDir)
        self.no_pad.toggled.connect(self.onSelectedPadBtn)
        self.no_dialog.toggled.connect(self.onSelectedDialogBtn)
        self.no_download.toggled.connect(self.onSelectedDownloadBtn)
        self.no_splunk.toggled.connect(self.onSelectedSplunkBtn)
        self.box_server_path.currentIndexChanged.connect(self.onSelectedServerPath)
        self.box_game_package.setCurrentIndex(0)
        self.box_game_package.currentIndexChanged.connect(self.onSelectedGamePackage)
        self.btn_config_release1.clicked.connect(self.onClickedReleaseConfig1)
        self.cb_release_flag.clicked.connect(self.onClickedReleaseFlag)
        self.btn_add_res.clicked.connect(self.onClickedAddRes)
        self.btn_config_res.clicked.connect(self.onClickedOpenResConfig)

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
        self.cb_release_flag.setChecked(self.selectedReleaseFlag)

    def initInfo(self):
        self.resetInfo()
        self.data = {
            debug_key[ConfigEnum.pad]: self.selectPad,
            debug_key[ConfigEnum.dialog]: self.selectDialog,
            debug_key[ConfigEnum.download]: self.selectDownload,
            debug_key[ConfigEnum.splunk]: self.selectSplunk,
            debug_key[ConfigEnum.server]: self.indexServerPath,
        }

    def resetInfo(self):
        self.selectPad = False
        self.selectDialog = False
        self.selectDownload = False
        self.selectSplunk = False
        self.selectHotupdate = False
        self.selectPackupdate = False
        self.indexServerPath = ServerUrlEnum.offline_test
        self.indexGamePackage = PlatformEnum.android
        self.selectedReleaseFlag = False

    def checkPathAndCallback(self, path, callback):
        if self.parent.checkProjectPath(path):
            callback()
        else:
            QMessageBox.critical(self, ERROR_TITLE, message_error[MessageError.project_path], QMessageBox.Ok)

    def saveConfig(self):
        self.common_signal.emit(DebugBoxError.save, self.name, self.getData())

    def deleteConfig(self):
        self.common_signal.emit(DebugBoxError.delete, self.name, self.getData())

    def openConfig(self):
        self.common_signal.emit(DebugBoxError.open, self.name, self.getData())

    def onClickedChangeConfig(self):
        def endFunc():
            self.saveConfig()
            print("修改配置执行完毕")

        self.checkPathAndCallback(self.path, endFunc)

    def onClickedResetConfig(self):
        def endFunc():
            self.resetData()
            self.updateUI()
            self.saveConfig()
            print("重置配置执行完毕")

        self.checkPathAndCallback(self.path, endFunc)

    def onClickedDeleteConfig(self):
        def endFunc():
            self.deleteConfig()

        self.checkPathAndCallback(self.path, endFunc)

    def onClickedOpenConfigDir(self):
        def endFunc():
            self.openConfig()

        self.checkPathAndCallback(self.path, endFunc)

    def onClickedReleaseConfig1(self):
        def endFunc():
            if not self.selectedReleaseFlag:
                return QMessageBox.warning(self, "警告", "请确认是否打包release包并勾选必选项", QMessageBox.Ok)
            self.selectPad = False
            self.selectDialog = False
            self.selectDownload = False
            self.selectSplunk = False
            self.indexServerPath = ServerUrlEnum.online
            self.updateUI()
            self.setHotUpdateAndPackUpdateSwitch()
            print("[屏蔽热更新|屏蔽资源包]执行完毕")

        self.checkPathAndCallback(self.path, endFunc)

    def onClickedReleaseFlag(self):
        self.selectedReleaseFlag = self.cb_release_flag.isChecked()

    def onSelectedPadBtn(self):
        self.selectPad = self.yes_pad.isChecked()

    def onSelectedDialogBtn(self):
        self.selectDialog = self.yes_dialog.isChecked()

    def onSelectedDownloadBtn(self):
        self.selectDownload = self.yes_download.isChecked()

    def onSelectedSplunkBtn(self):
        self.selectSplunk = self.yes_splunk.isChecked()

    def onSelectedServerPath(self, index):
        self.indexServerPath = index

    def onSelectedGamePackage(self, index):
        self.indexGamePackage = index
        self.updateGamePackageList()

    def onClickedAddRes(self):
        path = self.path
        game = self.parent.getGameGroup()

        def endFunc():
            res_path = QFileDialog.getExistingDirectory(self, "选取指定文件夹", path)
            dir_name = str(res_path)
            res_cdn = path + "/res_cdn"
            game_cdn = path + "/res_game/" + game + "/cdn"
            res_flag = dir_name.find(res_cdn) >= 0
            game_flag = dir_name.find(game_cdn) >= 0
            if dir_name and dir_name != "" and os.path.exists(dir_name) \
                    and dir_name != res_cdn and dir_name != game_cdn \
                    and (res_flag or game_flag):
                old_str = res_cdn + "/"
                dir_name = dir_name.replace(old_str, "")
                old_str = game_cdn + "/"
                dir_name = dir_name.replace(old_str, "")
                QListWidgetItem(dir_name, self.package_list_widget)

                if res_flag:
                    self.resCdn.append(dir_name)
                if game_flag:
                    self.gameCdn.append(dir_name)

                packages = game_package_names[game]
                package_config = path + "/res_game/config/" + packages[self.indexGamePackage] + "/config.properties"
                with open(package_config, "w") as fp:
                    fp.write("game_cdn=" + ":".join(self.gameCdn) + "\n")
                    fp.write("res_cdn=" + ":".join(self.resCdn))

                print("添加资源执行完毕，资源名=", dir_name)
            else:
                QMessageBox.critical(self, ERROR_TITLE, message_error[MessageError.res_cdn_path], QMessageBox.Ok)

        self.checkPathAndCallback(path, endFunc)

    def onClickedOpenResConfig(self):
        path = self.path

        def endFunc():
            game = self.parent.getGameGroup()
            packages = game_package_names[game]
            package_config = path + "/res_game/config/" + packages[self.indexGamePackage]
            OpenDir(package_config)

        self.checkPathAndCallback(path, endFunc)

    def getCdn(self, properties):
        gameCdn = []
        resCdn = []
        if os.path.isfile(properties):
            count = 1
            with open(properties, 'r') as f:
                for line in f.readlines():
                    if count == 1:
                        items = line.split('=')[1].replace("\n", "")
                        gameCdn = items.split(':')
                    if count == 2:
                        items = line.split('=')[1].replace("\n", "")
                        resCdn = items.split(':')
                    count += 1
        return gameCdn, resCdn

    def updateGamePackageList(self):
        self.gameCdn.clear()
        self.resCdn.clear()
        self.package_list_widget.clear()
        path = self.path
        if path and path != "":
            game = self.parent.getGameGroup()
            packages = game_package_names[game]
            package_config = path + "/res_game/config/" + packages[self.indexGamePackage] + "/config.properties"
            self.gameCdn, self.resCdn = self.getCdn(package_config)
            for game in self.gameCdn:
                if game and game != "":
                    QListWidgetItem(game, self.package_list_widget)
            for res in self.resCdn:
                if res and res != "":
                    QListWidgetItem(res, self.package_list_widget)

    def setHotUpdateAndPackUpdateSwitch(self):
        path = self.path

        def replaceSwitch(lua_file):
            if os.path.exists(lua_file):
                content = ReadFile(lua_file)
                content = re.sub(r"Native_path and Native_path.hotUpdateSwitchOff", "true", content)
                content = re.sub(r"Native_path and Native_path.runOnIosSimulator", "true", content)
                WritFile(lua_file, content)

        main_lua = path + "/src/main.lua"
        replaceSwitch(main_lua)
        pack_lua = path + "/src/framework/pack/PackUpdateControl.lua"
        replaceSwitch(pack_lua)

    def setVersionInfo(self):
        path = self.path
        if path and path != "":
            game = self.parent.getGameGroup()
            package = game_package_names[game]
            # android gp
            version, git_version = "nil", "nil"
            config_plist = path + common_config_path[game] + "config.plist"
            if os.path.exists(config_plist):
                content = ReadPlist(config_plist)
                git_version = content["gitVersion"] if content else "nil"
            self.lab_git_android.setText(git_version)
            config_platform = path + "/res_game/config/" + package[0] + "/platformConfig.lua"
            if os.path.exists(config_platform):
                content = ReadFile(config_platform)
                match_obj = re.search(r"Config\.version\s*=\s*\"(\d*\.\d*)\"", content)
                version = match_obj.group(1) if match_obj else "nil"
            self.lab_code_android.setText(version)
            # ios
            config_platform = path + "/res_game/config/" + package[1] + "/platformConfig.lua"
            if os.path.exists(config_platform):
                content = ReadFile(config_platform)
                match_obj = re.search(r"Config\.gitVersion\s*=\s*\"([^\"]*)\"", content)
                git_version = match_obj.group(1) if match_obj else "nil"
                match_obj = re.search(r"Config\.version\s*=\s*\"(\d*\.\d*)\"", content)
                version = match_obj.group(1) if match_obj else "nil"
            self.lab_git_ios.setText(git_version)
            self.lab_code_ios.setText(version)

    def setResInfo(self):
        path = self.path
        self.box_game_package.clear()
        if path and path != "":
            game = self.parent.getGameGroup()
            platformEnum = PlatformEnum.android
            for package_name in game_package_names[game]:
                self.box_game_package.insertItem(platformEnum, package_name)
                platformEnum += 1

    def updateInfo(self):
        debug = self.data.get(self.name)
        if debug:
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
        self.setVersionInfo()
        self.setResInfo()

    def setPath(self, path):
        super(DebugBox, self).setPath(path)
        self.saveConfig()


# 打包ipa框
class PackageBox(BaseBox, Ui_packageBox):

    def __init__(self, parent, name):
        super(PackageBox, self).__init__(parent, name)
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.btn_select_dir.clicked.connect(self.onClickedSelectDir)
        self.btn_upload_files.clicked.connect(self.onClickedUploadFiles)

    def onClickedSelectDir(self):
        path = QFileDialog.getExistingDirectory(self, "选择热更新文件夹", self.path or sys.path[0])
        tmpPath = str(path)

        def endFunc():
            self.textEdit_hotUpdate.setText(tmpPath)

        self.checkPathAndCallback(tmpPath, endFunc)

    def getHotUpdateZipPath(self):
        return self.textEdit_hotUpdate.toPlainText()

    def onClickedUploadFiles(self):
        zip_path = self.getHotUpdateZipPath()

        def upload():
            project_path = self.path
            server_path = project_path + "/tools/server"
            print("跳转到：" + server_path)
            if os.path.exists(server_path):
                os.chdir(server_path)
                print(os.getcwd())
                cmd = "python upload_update.py -d " + zip_path
                process = subprocess.Popen(cmd, shell=IS_MAC)
                process.wait()
            else:
                QMessageBox.critical(self, ERROR_TITLE, message_error[MessageError.not_exist_path] + ":" + server_path, QMessageBox.Ok)

        self.checkPathAndCallback(zip_path, upload)

    def checkPathAndCallback(self, path, callback):

        def checkWord():
            count = 0
            for tag in game_path_tag:
                word = path + "/" + game_path_tag[tag]
                if os.path.exists(word):
                    count += 1
            return count > 0

        if path and path != "" and checkWord():
            callback()
        else:
            QMessageBox.critical(self, ERROR_TITLE, message_error[MessageError.project_path], QMessageBox.Ok)


# game选择tab
class TabGroupView(QWidget, Ui_groupForm):
    common_signal = pyqtSignal(str)

    box_clz = {
        ItemEnum.debug: DebugBox,
        ItemEnum.ipa: PackageBox,
    }

    json_path = WORK_PATH + "/{0}_data.json"

    def __init__(self, game):
        super(TabGroupView, self).__init__()
        self.game = game
        self.box_handle = {
            ItemEnum.debug: self.handleDebug,
            ItemEnum.ipa: self.handleIPA,
        }
        self.boxs = []
        self.model = Model(self.json_path.format(self.game))
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
            # item
            item = ListItem(title)
            item.setSizeHint(QSize(ITEM_WIDTH, ITEM_HEIGHT))
            self.listWidget.addItem(item)
            # box
            box = self.box_clz[itemEnum](self, title)
            box.common_signal.connect(self.box_handle[itemEnum])
            self.boxs.append(box)
            self.stackedWidget.addWidget(box)
            itemEnum += 1
        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)
        self.listWidget.setCurrentRow(0)
        self.btn_setting.clicked.connect(self.onClickedSetProjectPath)
        self.btn_open.clicked.connect(self.onClickedOpenProjectPath)

    def onClickedSetProjectPath(self):
        path = QFileDialog.getExistingDirectory(self, "选择项目文件夹", sys.path[0])
        tmpPath = str(path)

        def endFunc():
            self.textEdit_path.setText(tmpPath)
            for box in self.boxs:
                box.setPath(tmpPath)

        self.checkPathAndCallback(tmpPath, endFunc)

    def onClickedOpenProjectPath(self):
        path = self.getProjectPath()
        self.checkPathAndCallback(path, lambda: OpenDir(path))

    def checkPathAndCallback(self, path, callback):
        if self.checkProjectPath(path):
            callback()
        else:
            QMessageBox.critical(self, ERROR_TITLE, message_error[MessageError.project_path], QMessageBox.Ok)

    def checkProjectPath(self, path):
        res_dir = path + "/res"
        src_dir = path + "/src"
        return path and path != "" and os.path.exists(res_dir) and os.path.exists(src_dir)

    def setProjectPath(self, path):
        text = path if path and path != "" else ""
        self.textEdit_path.setText(text)

    def getProjectPath(self):
        return self.textEdit_path.toPlainText()

    def handleDebug(self, cmd, name, data):
        path = self.getProjectPath()
        config_dir = path + debug_config_path[self.game]
        config_lua = config_dir + "selfConfig.lua"

        def saveConfig():
            self.model.save({name: data, "game": self.game, "path": path})

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

            with open(config_lua, 'w', encoding='utf-8') as fp:
                fp.write("Native_path =\n")
                fp.write("{\n")
                fp.write("\tsearchPath = {},\n")
                fp.write("\t{0} = true,\n".format(hotupdate_tag[self.game]))
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

        def deleteConfig():
            if os.path.exists(config_lua):
                os.remove(config_lua)
                print("删除配置文件执行完毕，配置路径=", config_lua)
            else:
                QMessageBox.critical(self, ERROR_TITLE, message_error[MessageError.config_lua], QMessageBox.Ok)

        def openConfigDir():
            if os.path.exists(config_dir):
                OpenDir(config_dir)
            else:
                QMessageBox.critical(self, ERROR_TITLE, message_error[MessageError.config_dir], QMessageBox.Ok)

        debug_handle = {
            DebugBoxError.save: saveConfig,
            DebugBoxError.delete: deleteConfig,
            DebugBoxError.open: openConfigDir,
        }

        handle = debug_handle[cmd]
        self.checkPathAndCallback(path, handle)

    def handleIPA(self, name, data):
        print("打包ipa")

    def getGameGroup(self):
        return self.game

    def getGamePath(self):
        return self.getProjectPath()


class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class DebugTools(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(DebugTools, self).__init__()
        self.setupUi(self)
        # 重定向输出
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        # info
        self.outInfo()
        # ui
        self.initUI()

    def normalOutputWritten(self, text):
        msg = text.replace('\r', '').replace('\n', '').replace('\t', '')
        if msg and msg != "":
            msg = "[{0}]: {1}".format(datetime.datetime.now(), msg)
            self.plainTextEdit.appendPlainText(msg)

    def outInfo(self):
        print("------------------------------------")
        print("用户目录:{0}".format(USER_PATH))
        print("工作目录:{0}".format(WORK_PATH))
        print("工作模式:{0}".format("debug" if IS_DEBUG_MODE else "release"))
        print("操作系统:{0}".format(sys.platform))
        print("------------------------------------")

    def initUI(self):
        self.plainTextEdit.setMaximumBlockCount(20)

        for title in tab_group_titles:
            self.tabWidget.addTab(TabGroupView(title), title)

        self.resize(UI_WIDTH, UI_HEIGHT)
        frame = self.frameGeometry()
        frame.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())
        self.setWindowTitle(UI_TITLE)
        print("初始化UI成功")

    def packageIPA(self):
        print("打包ipa")

    def uploadRes(self):
        print("上传资源")

    def closeWin(self):
        self.close()

    def destroy(self):
        self.close()

    def closeEvent(self, event):
        if IS_DEBUG_MODE:
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
    app.setWindowIcon(QIcon('./icon/128.ico'))
    tools = DebugTools()
    tools.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
