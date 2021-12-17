import datetime


class LogHelper:

    def __init__(self, config):
        self.config = config

    def __log(self, tag, msg):
        msg = msg.replace('\r', '').replace('\n', '').replace('\t', '')
        if msg and msg != "":
            msg = "[{0}][{1}]: {2}".format(tag, datetime.datetime.now(), msg)
            print(msg)

    def info(self, msg):
        self.__log("info", msg)

    def warning(self, msg):
        self.__log("warn", msg)

    def error(self, msg):
        self.__log("error", msg)