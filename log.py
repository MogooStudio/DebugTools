import os
import sys
import logging
import logging.handlers


class LogHelper:

    def __init__(self, config):
        root_path = config["root_path"]
        backup_count = config["backup_count"]
        max_bytes = config["max_bytes"]
        name = os.path.join(root_path, sys.argv[0].split('/')[-1].split('.')[0])
        self.log = logging.getLogger()
        fmt = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        handle_txt = logging.handlers.RotatingFileHandler(name, maxBytes=max_bytes, backupCount=backup_count)
        handle_txt.setFormatter(fmt)
        handle_screen = logging.StreamHandler(stream=sys.stdout)
        handle_screen.setFormatter(fmt)
        self.log.addHandler(handle_txt)
        self.log.addHandler(handle_screen)
        self.log.setLevel(logging.INFO)

    def info(self, msg):
        self.log.info(msg)

    def warning(self, msg):
        self.log.warning(msg)

    def error(self, msg):
        self.log.error(msg)