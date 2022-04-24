import base64
import os
import sys
import re
import plistlib
import shutil
from enum import IntEnum

import xlrd
from PyQt5.QtGui import QPixmap, QDesktopServices, QIcon, QColor, QPainterPath, QPainter, QImage, QDragEnterEvent, \
    QDropEvent
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QUrl, QStandardPaths, QTimer, QRectF, Qt
from PyQt5.QtWidgets import QSpacerItem, QListWidget, QLabel, QGridLayout, QHBoxLayout, QFileDialog, QDialog, \
    QGroupBox, QListWidgetItem, \
    QWidget, QApplication, QMainWindow, \
    QMessageBox, QDesktopWidget, QGraphicsDropShadowEffect, QSizePolicy

from changeToJsonBox import Ui_changeToJsonBox
from mainUI import Ui_MainWindow
from groupForm import Ui_groupForm
from debugBox import Ui_debugBox
from packageBox import Ui_packageBox
from crashDialog import Ui_crashDialog
from crashBox import Ui_crashBox

from model import Model
from log import LogHelper


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
LOG_PATH = WORK_PATH + "/log"
MakeDir(LOG_PATH)
TEMP_PATH = WORK_PATH + "/temp"
MakeDir(TEMP_PATH)


log_config = {
    "log_path": LOG_PATH,
    "backup_count": 10,
}
LOG = LogHelper(log_config)

UI_WIDTH = 1280
UI_HEIGHT = 900
ITEM_WIDTH = 150
ITEM_HEIGHT = 80

UI_TITLE = "调试工具"
ERROR_TITLE = "错误"
WARN_TITLE = "警告"
PROMPT_TITLE = "提示"


# 全局函数
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


# 枚举
class ItemEnum(IntEnum):
    debug = 1
    ipa = 2
    change = 3


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


class MessageWarn(IntEnum):
    package_release = 1


class DebugBoxError(IntEnum):
    save = 1
    delete = 2
    open = 3


class CrashBoxEnum(IntEnum):
    ips = 1
    dSYM = 2


tab_group_titles = ["game1", "game2", "game3"]

item_titles = {
    ItemEnum.debug: "调试配置",
    ItemEnum.ipa: "打包ipa",
    ItemEnum.change: "转换json",
}

crash_titles = {
    CrashBoxEnum.ips: "把ips拖入到框内",
    CrashBoxEnum.dSYM: "把ips拖入到框内",
}

crash_suffix = {
    CrashBoxEnum.ips: ".ips",
    CrashBoxEnum.dSYM: ".dSYM",
}

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

message_warn = {
    MessageWarn.package_release: "请确认是否打包release包并勾选必选项",
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
    ServerUrlEnum.online: {
        "game1": None,
        "game2": None,
        "game3": None,
    },
    ServerUrlEnum.offline_test: {
        "game1": "http://192.168.1.201/slots_server/www/hummer/debug/api.php",
        "game2": "http://192.168.1.201/slots_server/www/hummer/debug/api.php",
        "game3": "http://192.168.1.201/hm-game3/www/game3/debug/api.php",
    },
    ServerUrlEnum.online_test: {
        "game1": "http://ec2-35-160-211-175.us-west-2.compute.amazonaws.com/hummer_game/api",
        "game2": "http://ec2-35-160-211-175.us-west-2.compute.amazonaws.com/hummer_game/api",
        "game3": "http://ec2-52-33-159-0.us-west-2.compute.amazonaws.com/api",
    },
}

server_report_url = {
    ServerUrlEnum.online: {
        "game1": None,
        "game2": None,
        "game3": None,
    },
    ServerUrlEnum.offline_test: {
        "game1": "http://192.168.1.201/slots_server/www/hummer/debug/report.php",
        "game2": "http://192.168.1.201/slots_server/www/hummer/debug/report.php",
        "game3": "http://192.168.1.201/hm-game3/www/game3/debug/report.php",
    },
    ServerUrlEnum.online_test: {
        "game1": "http://ec2-35-160-211-175.us-west-2.compute.amazonaws.com/hummer_game/report",
        "game2": "http://ec2-35-160-211-175.us-west-2.compute.amazonaws.com/hummer_game/report",
        "game3": "http://ec2-52-33-159-0.us-west-2.compute.amazonaws.com/report",
    },
}

server_stat_url = {
    ServerUrlEnum.online: {
        "game1": None,
        "game2": None,
        "game3": None,
    },
    ServerUrlEnum.offline_test: {
        "game1": "http://192.168.1.201/slots_server/www/hummer/debug/stat.php",
        "game2": "http://192.168.1.201/slots_server/www/hummer/debug/stat.php",
        "game3": "http://192.168.1.201/hm-game3/www/game3/debug/stat.php",
    },
    ServerUrlEnum.online_test: {
        "game1": "http://ec2-35-160-211-175.us-west-2.compute.amazonaws.com/hummer_game/stat",
        "game2": "http://ec2-35-160-211-175.us-west-2.compute.amazonaws.com/hummer_game/stat",
        "game3": "http://ec2-52-33-159-0.us-west-2.compute.amazonaws.com/stat",
    },
}

server_terms_url = {
    ServerUrlEnum.online: {
        "game1": None,
        "game2": None,
        "game3": None,
    },
    ServerUrlEnum.offline_test: {
        "game1": "http://192.168.1.201/slots_server/www/hummer/debug/terms.php",
        "game2": "http://192.168.1.201/slots_server/www/hummer/debug/terms.php",
        "game3": "http://192.168.1.201/hm-game3/www/game3/debug/terms.php",
    },
    ServerUrlEnum.online_test: {
        "game1": "http://ec2-35-160-211-175.us-west-2.compute.amazonaws.com/hummer_game/terms",
        "game2": "http://ec2-35-160-211-175.us-west-2.compute.amazonaws.com/hummer_game/terms",
        "game3": "http://ec2-52-33-159-0.us-west-2.compute.amazonaws.com/terms",
    },
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


# 调试项目框
class DebugBox(BaseBox, Ui_debugBox):

    def __init__(self, parent, name):
        super(DebugBox, self).__init__(parent, name)
        self.gameCdn = []
        self.resCdn = []
        self.setupUi(self)
        self.resetInfo()
        self.initUI()
        self.updateUI()

    def initUI(self):
        self.btn_change_config.clicked.connect(self.onClickedChangeConfig)
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
            NotificationWindow.error(ERROR_TITLE, message_error[MessageError.project_path])

    def saveConfig(self):
        data = self.getData()
        self.common_signal.emit(DebugBoxError.save, self.name, data)

    def deleteConfig(self):
        self.common_signal.emit(DebugBoxError.delete, self.name, self.getData())

    def openConfig(self):
        self.common_signal.emit(DebugBoxError.open, self.name, self.getData())

    def onClickedChangeConfig(self):
        def endFunc():
            self.saveConfig()
            msg = "修改配置执行完毕"
            NotificationWindow.success(PROMPT_TITLE, msg, callback=lambda: LOG.info(msg))

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
                return QMessageBox.warning(self, WARN_TITLE, message_warn[MessageWarn.package_release], QMessageBox.Ok)
            self.selectPad = False
            self.selectDialog = False
            self.selectDownload = False
            self.selectSplunk = False
            self.indexServerPath = ServerUrlEnum.online
            self.updateUI()
            self.setHotUpdateAndPackUpdateSwitch()
            msg = "[屏蔽热更新|屏蔽资源包]执行完毕"
            NotificationWindow.success(PROMPT_TITLE, msg, callback=lambda: LOG.info(msg))

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
                    fp.write("res_cdn=" + ":".join(self.resCdn) + "\n")
                msg = "添加资源执行完毕，资源名={0}".format(dir_name)
                NotificationWindow.success(PROMPT_TITLE, msg, callback=lambda: LOG.info(msg))
            else:
                NotificationWindow.error(ERROR_TITLE, message_error[MessageError.res_cdn_path])

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
        data = self.data
        key = debug_key[ConfigEnum.pad]
        self.selectPad = data[key]
        key = debug_key[ConfigEnum.dialog]
        self.selectDialog = data[key]
        key = debug_key[ConfigEnum.download]
        self.selectDownload = data[key]
        key = debug_key[ConfigEnum.splunk]
        self.selectSplunk = data[key]
        key = debug_key[ConfigEnum.server]
        self.indexServerPath = data[key]
        self.updateUI()
        self.setResInfo()

    def getData(self):
        return {
            debug_key[ConfigEnum.pad]: self.selectPad,
            debug_key[ConfigEnum.dialog]: self.selectDialog,
            debug_key[ConfigEnum.download]: self.selectDownload,
            debug_key[ConfigEnum.splunk]: self.selectSplunk,
            debug_key[ConfigEnum.server]: self.indexServerPath,
        }


# 打包ipa框
class PackageBox(BaseBox, Ui_packageBox):

    def __init__(self, parent, name):
        super(PackageBox, self).__init__(parent, name)
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
            NotificationWindow.error(ERROR_TITLE, message_error[MessageError.project_path])

# 转换
class ChangeToJsonBox(BaseBox, Ui_changeToJsonBox):

    def __init__(self, parent, name):
        super(ChangeToJsonBox, self).__init__(parent, name)
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.btn_select_excel.clicked.connect(self.onClickedSelectPathExcel)
        self.btn_select_json.clicked.connect(self.onClickedSelectPathJson)
        self.btn_change.clicked.connect(self.onClickedChange)

    def onClickedSelectPathExcel(self):
        path = QFileDialog.getExistingDirectory(self, "选择Exel文件", self.path or sys.path[0])
        tmpPath = str(path)

        def endFunc():
            self.textEdit_ipa.setText(tmpPath)

        self.checkPathAndCallback(tmpPath, endFunc)

    def onClickedSelectPathJson(self):
        path = QFileDialog.getExistingDirectory(self, "选择json存放文件夹", self.path or sys.path[0])
        tmpPath = str(path)

        def endFunc():
            self.textEdit_pod.setText(tmpPath)

        self.checkPathAndCallback(tmpPath, endFunc)

    def getExcelPath(self):
        return self.textEdit_ipa.toPlainText()

    def getOutputPath(self):
        return self.textEdit_pod.toPlainText()

    def onClickedChange(self):
        excel_path = self.getExcelPath()
        def change():
            for excel in os.listdir(excel_path):
                if excel.find("~$") == -1:
                    if excel.endswith(".xlsx") | excel.endswith(".xls"):
                        ui_path = os.path.join(excel_path, excel)
                        fPath, fName = os.path.split(ui_path)
                        if os.path.isfile(ui_path):
                            self.makeTranslateData(ui_path, fPath, fName)
        self.checkPathAndCallback(excel_path, change)

    def makeTranslateData(self, fileName, fPath, fname):
        table_data = xlrd.open_workbook(fileName)
        count = 0;
        for i in range(len(table_data.sheets())):
            sheetnewTranslate = table_data.sheet_by_index(i)
            rowNew = sheetnewTranslate.nrows  # 行数
            colNew = sheetnewTranslate.ncols  # 列数

            jsonName = fPath + "/" + sheetnewTranslate.name + ".lua"
            f = open(jsonName, 'w+')
            f.write("Config = {\n")
            allStr = ""
            for i in range(rowNew):
                if i != 0:
                    tempStr = ""
                    for k in range(colNew):
                        if k != 0:
                            values = sheetnewTranslate.cell_value(i, k)
                            if k == 1:
                                tempStr = "{" + str(int(values))
                            else:
                                tempStr = tempStr + "," + str(int(values))
                    tempStr = "\t" + tempStr + "}"
                    allStr = allStr + tempStr + ",\n"
            f.write(allStr)
            f.write("}")
            f.close()
            count = count + 1
        if count == len(table_data.sheets()):
            NotificationWindow.error(PROMPT_TITLE, "转化成功！")

    def checkPathAndCallback(self, path, callback):
        if path and path != "" and os.path.isdir(path):
            callback()
        else:
            NotificationWindow.error(ERROR_TITLE, message_error[MessageError.project_path])

# game选择tab
class TabGroupView(QWidget, Ui_groupForm):
    common_signal = pyqtSignal(str)

    box_clz = {
        ItemEnum.debug: DebugBox,
        ItemEnum.ipa: PackageBox,
        ItemEnum.change: ChangeToJsonBox,
    }

    json_path = WORK_PATH + "/{0}_data.json"

    def __init__(self, game):
        super(TabGroupView, self).__init__()
        self.game = game
        self.box_handle = {
            ItemEnum.debug: self.handleDebug,
            ItemEnum.ipa: self.handleIPA,
            ItemEnum.change: self.handleJson,
        }
        self.boxs = []
        self.model = Model(self.json_path.format(self.game))
        self.setupUi(self)
        self.initUI()
        self.initData()

    def initData(self):
        data_game = self.model.load()
        if not data_game:
            return
        path = data_game['path']
        self.setProjectPath(path)
        for box in self.boxs:
            data_item = data_game.get(box.getName())
            box.setData(data_item)
            box.setPath(path)
            box.updateInfo()

    def initUI(self):
        itemEnum = ItemEnum(1)
        for name in item_titles.values():
            # item
            item = ListItem(name)
            item.setSizeHint(QSize(ITEM_WIDTH, ITEM_HEIGHT))
            self.listWidget.addItem(item)
            # box
            box = self.box_clz[itemEnum](self, name)
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
            NotificationWindow.error(ERROR_TITLE, message_error[MessageError.project_path])

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
            http_url = server_http_url[server][self.game]
            report_url = server_report_url[server][self.game]
            stat_url = server_stat_url[server][self.game]
            terms_url = server_terms_url[server][self.game]

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
                if http_url is not None:
                    fp.write("Config.httpServer = \"{0}\"\n".format(http_url))
                if report_url is not None:
                    fp.write("Config.reportURL = \"{0}\"\n".format(report_url))
                if report_url is not None:
                    fp.write("Config.statURL = \"{0}\"\n".format(stat_url))
                if terms_url is not None:
                    fp.write("Config.termsOfServiceURL = \"{0}\"\n".format(terms_url))
                fp.write(config_theme)

        def deleteConfig():
            if os.path.exists(config_lua):
                os.remove(config_lua)
                msg = "删除配置文件执行完毕"
                NotificationWindow.success(PROMPT_TITLE, msg, callback=lambda: LOG.info(msg))
            else:
                NotificationWindow.error(ERROR_TITLE, message_error[MessageError.config_lua])

        def openConfigDir():
            if os.path.exists(config_dir):
                OpenDir(config_dir)
            else:
                NotificationWindow.error(ERROR_TITLE, message_error[MessageError.config_dir])

        debug_handle = {
            DebugBoxError.save: saveConfig,
            DebugBoxError.delete: deleteConfig,
            DebugBoxError.open: openConfigDir,
        }

        handle = debug_handle[cmd]
        self.checkPathAndCallback(path, handle)

    def handleIPA(self, name, data):
        LOG.info("开始打包ipa")

    def handleJson(self, name, data):
        LOG.info("开始转换json")


    def getGameGroup(self):
        return self.game

    def getGamePath(self):
        return self.getProjectPath()


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


class ipsCrashBox(QGroupBox, Ui_crashBox):

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
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


# crash对话框
class CrashDialog(QDialog, Ui_crashDialog):

    def __init__(self):
        super(CrashDialog, self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.btn_parse.clicked.connect(self.parse)
        ips = ipsCrashBox()
        dSYM = dSYMCrashBox()
        self.widListLayout.addWidget(ips)
        self.widListLayout.addWidget(dSYM)

    def parse(self):
        crash_file = TEMP_PATH + "/AAA.crash"
        dSYM_file = TEMP_PATH + "/AAA.dSYM"
        if not os.path.exists(crash_file):
            NotificationWindow.error(ERROR_TITLE, crash_file + " 文件不存在")
        if not os.path.exists(dSYM_file):
            NotificationWindow.error(ERROR_TITLE, dSYM_file + " 文件不存在")
        # cmd = "export DEVELOPER_DIR=\"/Applications/XCode.app/Contents/Developer\""
        # os.popen(cmd)
        cmd = "find /Applications/Xcode.app -name symbolicatecrash -type f"
        ret = os.popen(cmd)
        ret = str(ret)
        if ret and os.path.exists(ret):
            symbolicatecrash = TEMP_PATH + "/symbolicatecrash"
            shutil.copyfile(ret, symbolicatecrash)
        cmd = "./symbolicatecrash " + crash_file + " " + dSYM_file + " > crash.log"
        ret = os.popen(cmd)
        print(ret)


class DebugTools(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(DebugTools, self).__init__()
        self.setupUi(self)
        self.outInfo()
        self.initUI()

    def outInfo(self):
        LOG.info("------------------------------------")
        LOG.info("用户目录:{0}".format(USER_PATH))
        LOG.info("工作目录:{0}".format(WORK_PATH))
        LOG.info("工作模式:{0}".format("debug" if IS_DEBUG_MODE else "release"))
        LOG.info("操作系统:{0}".format(sys.platform))
        LOG.info("------------------------------------")

    def initUI(self):
        self.openConfigAction.triggered.connect(self.openConfig)
        self.crashParseAction.triggered.connect(self.crashParse)

        for title in tab_group_titles:
            self.tabWidget.addTab(TabGroupView(title), title)

        self.resize(UI_WIDTH, UI_HEIGHT)
        frame = self.frameGeometry()
        frame.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frame.topLeft())
        self.setWindowTitle(UI_TITLE)
        LOG.info("初始化UI成功")

    def openConfig(self):
        OpenDir(WORK_PATH)

    def crashParse(self):
        print("crashParse")
        dialog = CrashDialog()
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

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
