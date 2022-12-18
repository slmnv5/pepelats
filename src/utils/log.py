import sys
from datetime import datetime
from typing import Dict

level: str = "WARN"
if "--debug" in sys.argv:
    level = "DEBUG"
if "--info" in sys.argv:
    level = "INFO"


class DumbLog:
    """ Simplest log, use redirection to file """
    levelDict: Dict[str, int] = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}

    def __init__(self, lvl: str):
        self.__level: int = self.levelDict.get(lvl, 3)
        print(f"Starting log: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", file=sys.stderr)

    def error(self, msg: str) -> None:
        if self.__level <= 3:
            print(msg, file=sys.stderr)

    def warn(self, msg: str) -> None:
        if self.__level <= 2:
            print(msg, file=sys.stderr)

    def info(self, msg: str) -> None:
        if self.__level <= 1:
            print(msg, file=sys.stderr)

    def debug(self, msg: str) -> None:
        if self.__level <= 0:
            print(msg, file=sys.stderr)

    def set_level(self, lvl: str) -> None:
        self.__level = self.levelDict.get(lvl, 3)


LOGGER = DumbLog(level)
