import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


class DumbLog:
    """ Simple log to file and to screen if DEBUG or INFO """
    __level_dict: Dict[str, int] = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}
    tmp = Path(__file__).parent.parent.parent
    tmp = os.path.join(tmp, "log.txt")
    __file = open(tmp, 'a')
    tmp = "WARN"
    if "--debug" in sys.argv:
        tmp = "DEBUG"
    elif "--info" in sys.argv:
        tmp = "INFO"
    __lvl: int = __level_dict[tmp]
    print(1111111111111111, 555555555)
    print(f"====Starting log: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", file=__file)
    __file.flush()

    @staticmethod
    def flush():
        DumbLog.__file.flush()

    @staticmethod
    def __report(msg: str) -> None:
        print(msg, file=DumbLog.__file)
        if DumbLog.__lvl < 2:
            print(msg, file=sys.stderr)

    @staticmethod
    def error(msg: str) -> None:
        if DumbLog.__lvl <= 3:
            DumbLog.__report("ERROR: " + msg)

    @staticmethod
    def warn(msg: str) -> None:
        if DumbLog.__lvl <= 2:
            DumbLog.__report("WARN: " + msg)

    @staticmethod
    def info(msg: str) -> None:
        if DumbLog.__lvl <= 1:
            DumbLog.__report("INFO: " + msg)

    @staticmethod
    def debug(msg: str) -> None:
        if DumbLog.__lvl <= 0:
            DumbLog.__report("DEBUG: " + msg)

    @staticmethod
    def set_level(lvl: str) -> None:
        if lvl not in DumbLog.__level_dict:
            return
        DumbLog.__lvl = DumbLog.__level_dict[lvl]
