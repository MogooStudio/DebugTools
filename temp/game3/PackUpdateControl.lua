PackUpdateControl = class("PackUpdateControl")

local DB_NAME = "login_screen.db"
local PACK_INFO_KEY  = "pack_info"
local PACK_CONFIG = "pack_config/config.json"
local MAX_FAIL_COUNT = 5
local AUTO_DOWNLOAD_INTERVAL = 5

local VIDIO_NAME = "video.mp4"

function PackUpdateControl:ctor()
    self.zipSize = nil
    self.isPlayVideo = false
	self.failCount = 0
	self.tblAssetsManager = {}
    self.videoState = VIDIO_PLAY_STATE.NotPlay
    hummer.existPack = self:checkVersion()
    release_print(string.format("hummer.existPack=%s", hummer.existPack and "true" or "false"))
end

function PackUpdateControl:getInstance()
    if not self._instance then
        self._instance = PackUpdateControl.new()
    end
    return self._instance
end

function PackUpdateControl:showView()
	if not self.view then
		self.view = PackUpdateView.new(self)
    	self.view:show()
	end
end

function PackUpdateControl:hideView()
	if self.view then
    	self.view:hide()
    	self.view = nil
	end
end

function PackUpdateControl:checkVersion()
    self.version = utils.getDBValue(PACK_INFO_KEY, DB_NAME)
    if Config.gitVersion and Config.gitVersion ~= "" and self.version and self.version ~= "" and Config.gitVersion == self.version then
        return true
    end
end

function PackUpdateControl:playVideo()
    if not tolua.isnull(self.view) and self.isPlayVideo then
        local videoFilePath = storagePath .. "/" .. VIDIO_NAME
        self.view:playVideo(videoFilePath)
    end
end

function PackUpdateControl:downloadVideo(serverPath, storagePath)
    if self.auditing then
        return
    end
    local path = string.format("%s", serverPath)
    local url = path .. VIDIO_NAME
    local xhr = cc.XMLHttpRequest:new()
    xhr.responseType = cc.XMLHTTPREQUEST_RESPONSE_STRING
    xhr:open("GET", url)
    local function onComplete()
        if xhr.readyState == 4 and (xhr.status >= 200 and xhr.status < 207) and xhr.response ~= "" then
            local data = xhr.response
            local videoFilePath = storagePath .. "/" .. VIDIO_NAME
            if not cc.FileUtils:getInstance():isFileExist(videoFilePath) then
                local f = io.open(videoFilePath, "wb")
                io.write(data)
                io.close(f)
            end
            if not tolua.isnull(self.view) and self.isPlayVideo then
                self.view:playVideo(videoFilePath)
            end
        end
    end
    xhr:registerScriptHandler(onComplete)
    xhr:send()
end

function PackUpdateControl:finishEnd()
	if self.videoState == VIDIO_PLAY_STATE.Playing then
        self.downloadFinish = true
        return
    end
    if Config.gitVersion and Config.gitVersion ~= "" then
        utils.setDBValue(PACK_INFO_KEY, Config.gitVersion, DB_NAME)
    end
	local function laterCall()
		self:hideView()
		if self.downloadEndCall then
			self.downloadEndCall()
			self.downloadEndCall = nil
		end
	end
	utils.scheduleGlobal(1, laterCall)
end

function PackUpdateControl:downloadZip(serverPath, downloadPath, zipName, md5Name, handleSuccess, handleProgress, handleError)
	if not string.find(serverPath, "^https?://") then
        return
    end

    local assetsManager
    local isNeedToDown = true
    if self.tblAssetsManager[zipName] then
        assetsManager = self.tblAssetsManager[zipName]
        isNeedToDown = false
    else
        assetsManager = cc.AssetsManager:new(serverPath .. zipName .. ".zip", serverPath .. md5Name .. ".md5?=" .. os.time(), downloadPath)
        assetsManager:retain()
        self.tblAssetsManager[zipName] = assetsManager
    end

    local function onSuccess()
        self.tblAssetsManager[zipName] = nil
        assetsManager:release()
        if handleSuccess then
            handleSuccess()
        end
    end

    local function onError(errorCode)
        self.tblAssetsManager[zipName] = nil
        if errorCode == cc.ASSETSMANAGER_NO_NEW_VERSION then
            onSuccess()
        elseif errorCode == cc.ASSETSMANAGER_NETWORK then
            assetsManager:release()
            if handleError then
                handleError(errorCode)
            end
        else
            assetsManager:release()
            if handleError then
                handleError(errorCode)
            end
        end
    end

    local function onProgress(percent)
        if handleProgress then
            handleProgress(percent)
        end
    end

    assetsManager:setDelegate(onError, cc.ASSETSMANAGER_PROTOCOL_ERROR)
    assetsManager:setDelegate(onProgress, cc.ASSETSMANAGER_PROTOCOL_PROGRESS)
    assetsManager:setDelegate(onSuccess, cc.ASSETSMANAGER_PROTOCOL_SUCCESS)

    if isNeedToDown then
        self.startDownloadPackRes = true
        assetsManager:setConnectionTimeout(15)
        assetsManager:checkUpdate()
    end
end

function PackUpdateControl:showNetworkDialog()
    local showDialog = device.platform == "windows" or (not utils.callJavaOrOc("checkNetworkConnected", {}, "()Z"))
    if showDialog then
        if not tolua.isnull(self.netErrorTip) then
            return
        end
        self.netErrorTip = NetErrorTipView.new()
        self.netErrorTip:show()
    end 
end

function PackUpdateControl:downloadPack(serverPath, zipName, md5Name, storagePath)
	if self.failCount >= MAX_FAIL_COUNT then
        self:showNetworkDialog()
	end

	local function onError(errorCode)
        release_print(string.format("pack download fail %d count", self.failCount))
        self.failCount = self.failCount + 1
        local totalSize = (self.zipSize or 20.01)
        if not self.curSize then
            self.curSize = string.format("%0.2f", 0)
            self.view:setDownloadPercent(0)
        end
        if not self.isReportFlag then
            self.isReportFlag = true
            if self.reportCallback then
                self.reportCallback("resource_package_verify", {["S"]=2,['V']=utils.getDBValue(PACK_INFO_KEY, DB_NAME) or ""})
            end
        end
        self.view:setDownloadText("DOWNLOADING", self.curSize, totalSize)
        utils.laterCallBackGlobal(AUTO_DOWNLOAD_INTERVAL, function() self:downloadPack(serverPath, Config.gitVersion, Config.gitVersion, storagePath) end)
    end

    local function onProgress(percent)
        local curPercent = percent
        release_print(string.format("pack downloading %d%%", percent))
        local totalSize = (self.zipSize or 20.01)
        self.curSize = string.format("%0.2f", totalSize / 100 * curPercent)
        self.view:setDownloadText("DOWNLOADING", self.curSize, totalSize)
        self.view:setDownloadPercent(percent)
    end

    local function onSuccess()
        release_print("pack download finish")
        self.view:setDownloadText("SUCCESS")
        self:finishEnd()
        if self.reportCallback then
            self.reportCallback("resource_package_verify", {["S"]=1,['V']=utils.getDBValue(PACK_INFO_KEY, DB_NAME)})
        end
    end

	self:downloadZip(serverPath, storagePath, zipName, md5Name, onSuccess, onProgress, onError)
end

function PackUpdateControl:checkUpdate(serverPath, storagePath)
    if true then
        release_print("native mode")
        self.view:setDownloadText("LOGIN")
        self:finishEnd()
        return
    end

    if hummer.existPack then
        release_print("pack exist")
        self.view:setDownloadText("LOGIN")
        self:finishEnd()
        return
    end

    local path = string.format("%s%d/", serverPath, self.auditing and 0 or 1)
    local url = Config.server .. PACK_CONFIG
    local xhr = cc.XMLHttpRequest:new()
    local scheduler = cc.Director:getInstance():getScheduler()
    local schedulerId = nil
    release_print("check pack config="..url)
    local function onDownload()
        release_print("check pack download="..path..Config.gitVersion..".zip")
        self:downloadPack(path, Config.gitVersion, Config.gitVersion, storagePath)
    end
    local function onTimeOut()
        scheduler:unscheduleScriptEntry(schedulerId)
        xhr:abort()
        onDownload()
    end
    schedulerId = scheduler:scheduleScriptFunc(onTimeOut, 10, false)
    xhr.responseType = cc.XMLHTTPREQUEST_RESPONSE_STRING
    xhr:open("GET", url)
    local function onComplete()
        scheduler:unscheduleScriptEntry(schedulerId)
        if xhr.readyState == 4 and (xhr.status >= 200 and xhr.status < 207) and xhr.response ~= "" then
            local str = xhr.response
            local data = json.decode(str)
            if data and data.zipInfo then
                local key = string.format("size_%d", self.auditing and 0 or 1)
                self.zipSize = data.zipInfo[key]
            end
            if data and data.playVideo then
                self.isPlayVideo = data.playVideo == 1
            end
        end
        onDownload()
    end
    xhr:registerScriptHandler(onComplete)
    xhr:send()
end

function PackUpdateControl:setPlayVideoState(state)
    self.videoState = state
    if self.videoState == VIDIO_PLAY_STATE.PlayEnd and self.downloadFinish then
        self:finishEnd()
    end
end

function PackUpdateControl:getPlayVideoState()
    return self.videoState
end

function PackUpdateControl:pubShowPackScreen(callback)
	self:showView()
    self.reportCallback = callback
    if hummer.existPack then
        if callback then
            callback("resource_package_verify",{["S"]=0,['V']=self.version})
        end
    end
end

function PackUpdateControl:pubDownloadPack(serverPath, storagePath, auditing, downloadEndCall)
    self.auditing = auditing
    self.downloadEndCall = downloadEndCall
    self:checkUpdate(serverPath, storagePath)
end

