
cc.FileUtils:getInstance():setPopupNotify(false)
cc.FileUtils:getInstance():addSearchPath("src")
cc.FileUtils:getInstance():addSearchPath("res")
math.randomseed(cc.utils:gettime())
writeLogToFile  = function(info) end
hummer          = hummer or {}
Config          = cc.FileUtils:getInstance():getValueMapFromFile("config.plist")
appDebugMode    = (hummer and hummer.getDebugMode and hummer.getDebugMode())
hummer.GameStartTime = cc.utils:gettime()


local _require = require
local mappingTablePath = "dw/ui/lobby/lobby_bg.webp"
local loadMappingTable = function()
    local fileInstance = cc.FileUtils:getInstance()
    local contents,jsonObj = "",{}
    if fileInstance:isFileExist(mappingTablePath) then
        local contents = fileInstance:getDataFromFile(mappingTablePath)
        contents = "return {" ..tostring(fileInstance:getDataFromFile(mappingTablePath)) .. "}"
        local status = xpcall(function()
            local func = loadstring(contents)
            if func then
                jsonObj = func()
            end
        end, function(e)
            
        end)
        if  status then
            require = function(path)
                if jsonObj[path] then
                    local _path = "dw/" .. jsonObj[path]
                    if fileInstance:isFileExist(_path) then
                        path = _path
                    end
                end
                return _require(path)
            end
        end
    end
end

if cc.FileUtils:getInstance():isFileExist("platformConfig.lua") or cc.FileUtils:getInstance():isFileExist("platformConfig.luac") then
    require "platformConfig"
end

local function localConfig()
    cc.FileUtils:getInstance():addSearchPath("/sdcard/hummer/config", true)
    if not Native_path then
        return
    end
    G_DB_USE_FILE_TAG          = Native_path.dbUseFileTag
    G_FORBID_SHOW_FPS_TAG      = Native_path.forbidShowFPSTag
    G_LOG_FORBID_PRINT_TAG     = Native_path.logForbidPrintTag
    G_THEME_DEVELOP_ID_LIST    = Native_path.themeDevelopIdList
    G_THEME_FORBID_PROTECT_TAG = Native_path.themeForbidProtectTag
    G_THEME_FORBID_SPECIAL_ICON= Native_path.themeForbidSpecialIcon
    if Native_path.searchPath then
        for key, var in pairs(Native_path.searchPath) do
            print("var is "..var)
            cc.FileUtils:getInstance():addSearchPath(var, true)
        end
    end
    if Native_path.logFilePath then
        local fileOut = io.open(Native_path.logFilePath, "w")
        if fileOut then
            fileOut:write("----start----\n")
            fileOut:close()
            writeLogToFile = function(info)
                if type(info)~="string" then return end
                local fileOut = io.open(Native_path.logFilePath, "a");
                if fileOut then
                    fileOut:write(info .. "\n")
                    fileOut:close()
                end
            end
            print_own = print
            print = function(info)
                print_own(info)
                writeLogToFile(info)
            end
        end
    end
end

if appDebugMode then
    DEBUG_QUICK_TEST_DOWLOALD_DIR = "debugGm"
    if cc.FileUtils:getInstance():isFileExist("selfConfig.lua") or cc.FileUtils:getInstance():isFileExist("selfConfig.luac") then
        require "selfConfig"
        Config.server = Native_path.server or Config.server
    end
    if cc.FileUtils:getInstance():isFileExist("debugConfig.lua") then
        require "debugConfig"
        Config.server = Native_path.server or Config.server
    end
    localConfig()
    local require_ = require
    require = function(path)
        assert(string.sub(path, string.len(path) - 3) ~= ".lua", "require \"" .. path .. "\" -- suffix \".lua\" is prohibited.")
        return require_(path)
    end
else
    print = function(info) end
end
require "config"
require "cocos.init"
require "app.loginScreen.init"
require "app.updateDialog.init"
require "hummer.plugins.Facebook"
require "hummer.plugins.AppleLogin"
function cc.Scene:push( ... ) end
function cc.Scene:pop( ... ) end
function cc.Scene:onPause( ... ) end
function cc.Scene:onResume( ... ) end

local tblPlatformNames = {
    ["android"] = "android",
    ["windows"] = "win",
    ["ios"]     = "win",
    ["mac"]     = "win",
}
local platformName  = tblPlatformNames[device.platform]
hummer.updatePath   = string.format("update_%s/", platformName)
if device.platform == "ios" then
    hummer.updatePath = "res_dw_win/"
end
Config.gitVersion   = Config.gitVersion .. platformName

local assetsManager = nil
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
    if Config.channel ~= "avidly" then
        return
    end
    if device.platform == "android" then
        local luaj = require "cocos.cocos2d.luaj"
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
    if Config.channel ~= "avidly" or device.platform ~= "android" then
        return
    end
    local luaj = require "cocos.cocos2d.luaj"
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

local function _enterGame( ... )
    local root = cc.FileUtils:getInstance():getWritablePath()
    hummer.resourceRoot = root..Config.cachedir.."/"
    hummer.addSearchPath(hummer.resourceRoot,true)
    for _,v in pairs({"theme_logo", "theme_resource"}) do
        cc.FileUtils:getInstance():createDirectory(hummer.resourceRoot..v)
        hummer.addSearchPath(hummer.resourceRoot..v,true)
        hummer.addSearchPath("res/"..v,false)
    end
    hummer.addSearchPath("/sdcard/hummer/"..Config.package.."/src",true)
    hummer.addSearchPath("/sdcard/hummer/"..Config.package.."/res",true)
    if DEBUG_QUICK_TEST_DOWLOALD_DIR then
        hummer.addSearchPath(hummer.resourceRoot .. DEBUG_QUICK_TEST_DOWLOALD_DIR .. "/src",true)
        hummer.addSearchPath(hummer.resourceRoot .. DEBUG_QUICK_TEST_DOWLOALD_DIR .. "/res",true)
    end

    local scheduler = cc.Director:getInstance():getScheduler()
    local schedulerId = nil
    loadMappingTable()
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
    if assetsManager then
        assetsManager:release()
        assetsManager = nil
    end
    hummer.getHotUpdatePercent = nil
    hummer.abortHotUpdate = nil
end

local function setHotUpdateVersion(version)
    local lastData = string.split(string.split(version, "_")[2], "-")[1]
    Config.lastHotUpdateVersion = lastData
end

local function setHotUpdateOldVersion(version)
    local oldData = string.split(string.split(version, "_")[2], "-")[1]
    Config.oldHotUpdateVersion = oldData
end

local function hotUpdate()
    LoginScreenControl:getInstance():pubResumeLoading()
    local startTime = os.clock()
    local curPercent = 0
    local function onError(errorCode)
        _logEvent("E04", os.clock() - startTime, {['R'] = curPercent, ['E'] = errorCode})
        if errorCode == cc.ASSETSMANAGER_NO_NEW_VERSION then
            release_print("no new version")
        elseif errorCode == cc.ASSETSMANAGER_NETWORK then
            hummer.loadError = 1
            release_print("network error")
        elseif errorCode == cc.ASSETSMANAGER_UNCOMPRESS then
            hummer.loadError = 3
            release_print("uncomppress error")
        end
        if not hummer.abortHotUpdate then
            return
        end
        _enterGame()
    end
    local function onProgress(percent)
        curPercent = percent
        release_print(string.format("downloading %d%%", percent))
        if hummer.getHotUpdatePercent then
            LoginScreenControl:getInstance():pubSetDownloadPercent(percent)
        end
    end
    local function onSuccess()
        release_print("downloading ok")
        local lastVersion = assetsManager:getVersion()
        _logEvent("E03", os.clock() - startTime, {['C'] = lastVersion})
        if lastVersion then
            setHotUpdateVersion(lastVersion)
            hummer.lastVersion = lastVersion
        end
        _enterGame()
    end    
    assetsManager:setDelegate(onError, cc.ASSETSMANAGER_PROTOCOL_ERROR )
    assetsManager:setDelegate(onProgress, cc.ASSETSMANAGER_PROTOCOL_PROGRESS)
    assetsManager:setDelegate(onSuccess, cc.ASSETSMANAGER_PROTOCOL_SUCCESS )
    assetsManager:checkUpdate()
    hummer.getHotUpdatePercent = function ()
        return curPercent
    end
    hummer.abortHotUpdate = function ()
        hummer.abortHotUpdate = nil
        if curPercent > 90 then
            return
        end
        _logEvent("E04", os.clock() - startTime, {['R'] = curPercent, ['E'] = "timeOut"})
        assetsManager:setAborted()
        assetsManager = nil
        _enterGame()
        hummer.loadError = 1
    end
end

local function resetUpdateInfo(pathToSave)
    assetsManager:setVersion(Config.gitVersion)
    setHotUpdateVersion(Config.gitVersion)
    cc.FileUtils:getInstance():removeDirectory(pathToSave .. "/src/")
    cc.FileUtils:getInstance():removeDirectory(pathToSave .. "/res/")
end

local function checkOldUpdate()
    local lastVersion = assetsManager:getVersion()
    release_print("last:" .. lastVersion .. " | curr:" .. Config.gitVersion)
    if lastVersion == "" then
        setHotUpdateVersion(Config.gitVersion)
        setHotUpdateOldVersion(Config.gitVersion)
        return true
    else
        setHotUpdateVersion(lastVersion)
        setHotUpdateOldVersion(lastVersion)
    end
    if lastVersion == Config.gitVersion then
        return false
    end
    local lastData = string.split(string.split(lastVersion, "_")[1], "-")
    local currData = string.split(string.split(Config.gitVersion, "_")[1], "-")
    for i = 1, #lastData do
        if tonumber(lastData[i]) < tonumber(currData[i]) then
            return true
        end
        if tonumber(lastData[i]) > tonumber(currData[i]) then
            return false
        end
    end
    return false
end

local function cleanOldHotUpdateDirectory()
    local oldDirName = cc.FileUtils:getInstance():getWritablePath() .. "hummerUpdate"
    if cc.FileUtils:getInstance():isDirectoryExist(oldDirName) then
        cc.FileUtils:getInstance():removeDirectory(oldDirName)
        return true
    end
end

local function checkVersion()
    release_print("version:" .. Config.version)
    local pathToSave = hummer.createDownloadDir()
    hummer.addSearchPath(pathToSave .. "/src", true)
    hummer.addSearchPath(pathToSave .. "/res", true)
    local script_server = Config.server .. hummer.updatePath

    print("hummer.resourceServer=" .. hummer.resourceServer)
    print("script_server=" .. script_server)
    assetsManager = cc.AssetsManager:new(script_server .. "DYNAMICALLY_REPLACED_FILE_NAME.zip", script_server .. Config.md5 .. ".md5", pathToSave)
    assetsManager:retain()
    if cleanOldHotUpdateDirectory() then
        resetUpdateInfo(pathToSave)
    end
    if checkOldUpdate() then
        resetUpdateInfo(pathToSave)
    end
    if true then
        _enterGame()
        return
    end
    local url = Config.statLoginURL .. "/" .. Config.package .. "/" .. Config.version .. "/" .. os.time()
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
            UpdateDialogControl:getInstance():pubCheckUpdate(versions, hotUpdate)
        else
            _logEvent("E02", os.clock() - startTime, {['O'] = 0, ['R'] = xhr.readyState, ['S'] = xhr.status})
            _enterGame()
        end
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
    _logEventForAvidly("T01")
    _firebaseLogEventForAvidly("T01")
    getServerTime()
    local director          = cc.Director:getInstance()
    local scene             = cc.Scene:create()
    hummer.scene            = scene
    hummer.resourceServer   = Config.server .. "res_cdn/"
    hummer.startLoadTime = os.time()
    director:runWithScene(hummer.scene)
    if LoginScreenControl:getInstance():pubIsFirstLogin() then
        hummer.isFirstLogin = true
    end
    _logEventForAvidly("T011", hummer.isFirstLogin and 1 or 0)

    local isGame2IosSpecial = false
    if Config.package == "slots.free.vegas.casino.jackpot.link.ios" then
        isGame2IosSpecial = true
    end

    if not isGame2IosSpecial then
        LoginScreenControl:getInstance():pubShowLoginScreen()
    end
    
    local scheduler = cc.Director:getInstance():getScheduler()
    local schedulerId = nil
    local function laterCall()
        if isGame2IosSpecial then
            local writepath = cc.FileUtils:getInstance():getWritablePath().. "res/"
            print("writepath: ".. writepath) 
            hummer.addSearchPath(writepath, true)
            LoginScreenControl:getInstance():pubShowLoginScreen()
        end

        scheduler:unscheduleScriptEntry(schedulerId)
        local eventDispatcher = scene:getEventDispatcher()
        local listener = cc.EventListenerKeyboard:create()
        local function onKeyReleased(keyCode, event)
            if keyCode == cc.KeyCode.KEY_BACK then
                --cc.Director:getInstance():endToLua()
            end
        end
        listener:registerScriptHandler(onKeyReleased, cc.Handler.EVENT_KEYBOARD_RELEASED )
        eventDispatcher:addEventListenerWithSceneGraphPriority(listener, scene)
        if hummer.isFirstLogin then
            setHotUpdateVersion(Config.gitVersion)
            -- _enterGame()
        end
        checkVersion()
    end
    schedulerId = scheduler:scheduleScriptFunc(laterCall, 0, false)
end

local status, msg = xpcall(main, __G__TRACKBACK__)
if not status then
    release_print(msg)
end

gAdjustAttribution = {}

function onAdjustAttributionCallback(data)
    if type(data) ~= 'table' then
        return
    end
    gAdjustAttribution.data = data
    if gAdjustAttribution.callback then
        gAdjustAttribution.callback(data)
    end
end
