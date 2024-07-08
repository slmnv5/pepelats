import logging
import os
import sys


class MyLog:
    __instance = None
    __fmt_str = "%(asctime)s;%(levelname)s>>>%(message)s"

    def __new__(cls):
        """ creates a singleton object, if it is not created, else returns existing """
        if not cls.__instance:
            cls.__instance = super(MyLog, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self._logger = logging.getLogger()
        for h in self._logger.handlers:
            self._logger.removeHandler(h)
        formatter = logging.Formatter(fmt=self.__fmt_str, datefmt="%Y-%m-%d %H:%M:%S")
        fname: str = "./log.txt"

        self._logger.addHandler(logging.FileHandler(fname, mode='a'))
        self._logger.addHandler(logging.StreamHandler(sys.stderr))
        for h in self._logger.handlers:
            h.setFormatter(formatter)

        if "--debug" in sys.argv:
            level = logging.DEBUG
        elif "--info" in sys.argv:
            level = logging.INFO
        else:
            level = logging.WARNING

        self._logger.setLevel(level)
        self.warning(f"=========== Started logger in process id: {os.getpid()} ==========")

    def debug(self, msg):
        self._logger.debug(msg)

    def info(self, msg):
        self._logger.info(msg)

    def warning(self, msg):
        self._logger.warning(msg)

    def error(self, msg):
        self._logger.error(msg)

    def exception(self, msg):
        self._logger.exception(msg)
