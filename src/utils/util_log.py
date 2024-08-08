import logging
import os
import sys
from datetime import datetime
from multiprocessing import Queue

from utils.util_name import AppName


class NoMidiInputFound(RuntimeError):
    pass


class ConfigError(RuntimeError):
    pass


class MyLog:
    __instance = None
    __fmt_str = "%(asctime)s;%(levelname)s>>>%(message)s"

    tmp = os.getcwd()
    pos = tmp.find(AppName.app_name)
    if pos >= 0:
        __fname = tmp[:pos + len(AppName.app_name)] + os.sep + "log.txt"
    else:
        __fname = "./log.txt"

    def __new__(cls):
        """ creates a singleton object """
        if not cls.__instance:
            cls.__instance = super(MyLog, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self.level = logging.WARNING
        self.__queue: Queue | None = None  # to send message to MVC view
        self._logger = logging.getLogger()
        for h in self._logger.handlers:
            self._logger.removeHandler(h)

        self._formatter = logging.Formatter(fmt=self.__fmt_str, datefmt="%Y-%m-%d %H:%M:%S")
        h = logging.FileHandler(self.__fname, mode='a')
        h.setFormatter(self._formatter)
        self._logger.addHandler(h)
        h = logging.StreamHandler(sys.stdout)
        self._logger.addHandler(h)

        if AppName.dash_debug in sys.argv:
            self.level = logging.DEBUG
        elif AppName.dash_info in sys.argv:
            self.level = logging.INFO
        else:
            self.level = logging.WARNING

        self._logger.setLevel(self.level)
        self._logger.log(logging.INFO, f"============= Start log at {datetime.now()},"
                                       f" level: {logging.getLevelName(self.level)}")

    def _write_to_screen(self, msg) -> None:
        if self.__queue:
            self.__queue.put([AppName.client_log, str(msg)])

    def debug(self, msg):
        if self.level <= logging.DEBUG:
            self._logger.debug(msg)
            self._write_to_screen(msg)

    def info(self, msg):
        if self.level <= logging.INFO:
            self._logger.info(msg)
            self._write_to_screen(msg)

    def warning(self, msg):
        if self.level <= logging.WARNING:
            self._logger.warning(msg)
            self._write_to_screen(msg)

    def error(self, msg):
        self._logger.error(msg)
        self._write_to_screen(msg)

    def exception(self, msg):
        self._logger.exception(msg)
        self._write_to_screen(msg)

    def set_screen_queue(self, queue: Queue) -> None:
        self.__queue = queue


MY_LOG = MyLog()

if __name__ == "__main__":
    pass
