cc.FileUtils:getInstance():setPopupNotify(false)
cc.FileUtils:getInstance():addSearchPath("src")
cc.FileUtils:getInstance():addSearchPath("res")
math.randomseed(cc.utils:gettime())
writeLogToFile  = function(info) end
hummer          = hummer or {}
Config          = cc.FileUtils:getInstance():getValueMapFromFile("framework/config.plist")
appDebugMode    = (hummer and hummer.getDebugMode and hummer.getDebugMode())
hummer.GameStartTime = cc.utils:gettime()

if cc.FileUtils:getInstance():isFileExist("platformConfig.lua") or cc.FileUtils:getInstance():isFileExist("platformConfig.luac") then
    require "platformConfig"
end

if appDebugMode then
    if cc.FileUtils:getInstance():isFileExist("framework/devMode/DebugModeConfig.lua") or cc.FileUtils:getInstance():isFileExist("framework/devMode/DebugModeConfig.luac") then
        require "framework/devMode/DebugModeConfig"
    end
    local require_ = require
    require = function(path)
        assert(string.sub(path, string.len(path) - 3) ~= ".lua", "require \"" .. path .. "\" -- suffix \".lua\" is prohibited.")
        return require_(path)
    end
else
    print = function(info) end
end

require "framework.init"

local tblPlatformNames = {
    ["android"] = "android",
    ["windows"] = "android",
    ["ios"]     = "win",
    ["mac"]     = "win",
}
local platformName = tblPlatformNames[device.platform]
Config.gitVersion = Config.gitVersion .. platformName
local enteredGame = false

local function _jsonNeedDecode(key,value)
    local newData = value
    local needDecode = {
        ["iabPurchaseOriginalJson"] =  true,
        ["extraInfo"] =  true,
    }
    if needDecode[key] then
        newData = json.decode(value)
    end
    return newData
end

local function _getStrByTbl(tbl)
    local newStr = ""
    local isFirst = true
    local function addStr(key,value)
        newStr = newStr .. key .. "=" ..tostring(value) .. ","
    end
    local function findStr(data ,sign)
        for k , value in pairs(data) do
            value = _jsonNeedDecode(k, value)
            if type(value)~="table" then   
                local key =  sign and sign .. "." .. k or k 
                addStr(key,value)
            else
                if isFirst then
                    isFirst = false
                    findStr(value)
                else
                    local key =  sign and sign .. "." .. k or k
                    findStr(value,key)
                end                
            end
        end
    end
    findStr(tbl)
    newStr = string.sub(newStr, 1, -2)
    return newStr
end

local function _logEvent(eventName, value, params)
    local info = {
        ['v'] = value,
        ['h_P'] = Config.version,
        ['h_G'] = Config.lastHotUpdateVersion,
        ['params'] = params
    }
    local newStr = _getStrByTbl(info)
    local tbl = {
        ['u'] = -1,
        ['k'] = -1,
        ['p'] = Config.statId,
        ['c'] = {
            ['e'] = eventName, 
            ['d'] = os.time() .. " t=" .. os.time() .. "," .. newStr
        }
    }
    local hashKey = hummer.encodeString(json.encode(tbl))
    local xhr = cc.XMLHttpRequest:new()
    xhr.responseType = cc.XMLHTTPREQUEST_RESPONSE_STRING
    xhr:open("POST", Config.statURL)
    local function onResponse()
        xhr:unregisterScriptHandler()
    end
    xhr:registerScriptHandler(onResponse)
    xhr:send("k=" .. hashKey)
end

local function _logEventForAvidly(eventName, value)
    if device.platform == "android" then
        local luaj = require "framework.cocos.cocos2d.luaj"
        local className = "com/hummer/holaanalysis/HummerHolaAnalysis"
        local funcName = "log"
        local sig   = nil
        local args  = nil
        if value then
            sig = "(Ljava/lang/String;Ljava/lang/String;)V"
            if type(value) == "table" then
                funcName = "logMap"
                args = {eventName, json.encode(value)}
            else
                args = {eventName, tostring(value)}
            end
        else
            sig = "(Ljava/lang/String;)V"
            args = {eventName}
        end
        luaj.callStaticMethod(className, funcName, args, sig)
    end
end

local function _firebaseLogEventForAvidly(eventName,params)
    if device.platform == "android" then
        local luaj = require "framework.cocos.cocos2d.luaj"
        local className = "com/hummer/common/LuaCommon"
        local funcName = "firebaseTrackEvent"
        local tbl = {}
        local result = ""
        local sig = "(Ljava/lang/String;Ljava/lang/String;)V"
        if type(eventName) ~= "string" then
            return
        end
        if type(params) == "table" then
            result = json.encode(params)
        elseif params ~= nil then
            tbl = {default = tostring(params)}
            result = json.encode(tbl)
        end
        local ok, ret = luaj.callStaticMethod(className, funcName, {eventName,result},sig)
        if not ok then
            return
        end
        return ret
    end
end

local function _enterGame( ... )
    local root = cc.FileUtils:getInstance():getWritablePath()
    hummer.resourceRoot = root..Config.cachedir.."/"
    hummer.addSearchPath(hummer.resourceRoot,true)
    for _,v in pairs({"theme_logo", "theme_resource"}) do
        cc.FileUtils:getInstance():createDirectory(hummer.resourceRoot..v)
        hummer.addSearchPath(hummer.resourceRoot..v,true)
        hummer.addSearchPath("res/"..v,false)
    end
    HotUpdateTool.trySetRequireJpgHiddenLuaFileByIos()
    hummer.addSearchPath("/sdcard/hummer/"..Config.package.."/src",true)
    hummer.addSearchPath("/sdcard/hummer/"..Config.package.."/res",true)
    if DEBUG_QUICK_TEST_DOWLOALD_DIR then
        hummer.addSearchPath(hummer.resourceRoot .. DEBUG_QUICK_TEST_DOWLOALD_DIR .. "/src",true)
        hummer.addSearchPath(hummer.resourceRoot .. DEBUG_QUICK_TEST_DOWLOALD_DIR .. "/res",true)
    end

    local scheduler = cc.Director:getInstance():getScheduler()
    local schedulerId = nil
    local function laterCall()
        scheduler:unscheduleScriptEntry(schedulerId)
        if enteredGame then
            return
        end
        enteredGame = true
        if not xpcall(function() require "entrance" end, __G__TRACKBACK__) then
            hummer.loadError = 2
            local value = {
                ['F'] = hummer.isFirstLogin and 1 or 0,
                ['E'] = 2,
            }
            _logEventForAvidly("T013", value)
        end
        g_enter_game_login()
    end
    local function callback()
        schedulerId = scheduler:scheduleScriptFunc(laterCall, 1, false)
    end
    LoginScreenControl:getInstance():pubHotUpdateEnd(callback)
end

local function checkVersion()
    release_print("version:" .. Config.version)
    HotUpdateEx.pubInitBaseInfo()
    if true then
        _enterGame()
        return
    end

    local url = Config.statLoginURL .. "/" .. Config.package .. "/" .. Config.version .. "/" .. os.time()
    if appDebugMode then
        Config.statLoginURL = "http://192.168.1.201/hm-game3/www/game3/debug/stat.php"
        url = Config.statLoginURL .. "?p=" .. Config.package .. "&v=" .. Config.version
    end
    
    local xhr = cc.XMLHttpRequest:new()
    local scheduler = cc.Director:getInstance():getScheduler()
    local schedulerId = nil
    local startTime = os.clock()
    local function onTimeOut()
        _logEvent("E02", os.clock() - startTime, {['O'] = 1})
        scheduler:unscheduleScriptEntry(schedulerId)
        xhr:abort()
        _enterGame()
        hummer.loadError = 1
    end
    schedulerId = scheduler:scheduleScriptFunc(onTimeOut, 10, false)
    xhr.responseType = cc.XMLHTTPREQUEST_RESPONSE_STRING
    xhr:open("GET", url)
    hummer.auditing = true
    local function onDownload()
        scheduler:unscheduleScriptEntry(schedulerId)
        LoginScreenControl:getInstance():pubOnGotVersion()
        if xhr.readyState == 4 and (xhr.status >= 200 and xhr.status < 207) and xhr.response ~= "" then
            hummer.auditing = false
            _logEvent("E01", os.clock() - startTime)
            local versions = xhr.response
            LoginScreenControl:getInstance():pubPauseLoading()
            UpdateDialogControl:getInstance():pubCheckUpdate(versions, function( ... )
                HotUpdateEx.tryHotUpdate(_enterGame, _logEvent)
            end)
        else
            _logEvent("E02", os.clock() - startTime, {['O'] = 0, ['R'] = xhr.readyState, ['S'] = xhr.status})
            _enterGame()
        end
    end
    xhr:registerScriptHandler(onDownload)
    xhr:send()
end

local function checkPack()
    local pathToSave = utils.createDirectory("hummerPackRes")
    hummer.addSearchPath(pathToSave .. "/src", true)
    hummer.addSearchPath(pathToSave .. "/res", true)
    local packDir = cc.FileUtils:getInstance():getWritablePath()..Config.packdir.."/"
    hummer.addSearchPath(packDir, true)

    local function switchScene()
        LoginScreenControl:getInstance():pubShowLoginScreen()
        utils.scheduleGlobal(0, function() checkVersion() end)
    end

    local function downloadPack(auditing)
        local packSvrPath = Config.server .. string.format("pack_%s/", platformName)
        print("packSvrPath=" .. packSvrPath)
        _logEvent("resource_package_verify", hummer.existPack and 1 or 0)
        PackUpdateControl:getInstance():pubDownloadPack(packSvrPath, pathToSave, auditing, switchScene)
    end

    local url = Config.statLoginURL .. "/" .. Config.package .. "/" .. Config.version .. "/" .. os.time()
    local xhr = cc.XMLHttpRequest:new()
    local scheduler = cc.Director:getInstance():getScheduler()
    local schedulerId = nil
    local function onTimeOut()
        scheduler:unscheduleScriptEntry(schedulerId)
        xhr:abort()
        downloadPack(true)
    end
    schedulerId = scheduler:scheduleScriptFunc(onTimeOut, 10, false)
    xhr.responseType = cc.XMLHTTPREQUEST_RESPONSE_STRING
    xhr:open("GET", url)
    local function onDownload()
        scheduler:unscheduleScriptEntry(schedulerId)
        local audited = not (xhr.readyState == 4 and (xhr.status >= 200 and xhr.status < 207) and xhr.response ~= "")
        downloadPack(audited)
    end
    xhr:registerScriptHandler(onDownload)
    xhr:send()
end

local function getServerTime()
    local xhr = cc.XMLHttpRequest:new()
    xhr.responseType = cc.XMLHTTPREQUEST_RESPONSE_STRING
    xhr:open("POST", Config.httpServer)
    local function onResponse()
        if xhr.readyState == 4 and (xhr.status >= 200 and xhr.status < 207) then
            hummer.startServerTime = tonumber(xhr.response)
            if not hummer.startServerTime then
                return
            end
            hummer.startOsTime = hummer.getElapsedRealtime()
        end
        xhr:unregisterScriptHandler()
    end
    xhr:registerScriptHandler(onResponse)
    xhr:send("a=t")
end

local function main()
    ccexp.AudioEngine:play2d("hcommonSounds/welcome_open_app.mp3", false, 1)
    _logEventForAvidly("T01")
    _firebaseLogEventForAvidly("T01")
    getServerTime()
    local director = cc.Director:getInstance()
    local scene = cc.Scene:create()
    hummer.scene = scene
    hummer.startLoadTime = os.time()
    director:runWithScene(hummer.scene)
    if LoginScreenControl:getInstance():pubIsFirstLogin() then
        hummer.isFirstLogin = true
    end
    _logEventForAvidly("T011", hummer.isFirstLogin and 1 or 0)
    PackUpdateControl:getInstance():pubShowPackScreen(_logEvent)
    local scheduler = cc.Director:getInstance():getScheduler()
    local schedulerId = nil
    local function laterCall()
        scheduler:unscheduleScriptEntry(schedulerId)
        if hummer.isFirstLogin then
            HotUpdateTool.setHotUpdateVersion(Config.gitVersion)
        end
        checkPack()    
    end
    schedulerId = scheduler:scheduleScriptFunc(laterCall, 0, false)
end  

local status, msg = xpcall(main, __G__TRACKBACK__)
if not status then
    release_print(msg)
end