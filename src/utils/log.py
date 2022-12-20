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
    print(f"====Starting log: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", file=__file)
    __file.flush()

    @staticmethod
    def __report(msg: str) -> None:
        print(msg, file=logging.__file, flush=True)
        if logging.__lvl < 2:
            print(msg, file=sys.stderr)

    @staticmethod
    def error(msg: str) -> None:
        if logging.__lvl <= 3:
            logging.__report("PY-ERROR: " + msg)

    @staticmethod
    def warn(msg: str) -> None:
        if logging.__lvl <= 2:
            logging.__report("PY-WARN: " + msg)

    @staticmethod
    def info(msg: str) -> None:
        if logging.__lvl <= 1:
            logging.__report("PY-INFO: " + msg)

    @staticmethod
    def debug(msg: str) -> None:
        if logging.__lvl <= 0:
            logging.__report("PY-DEBUG: " + msg)

    @staticmethod
    def set_level(lvl: str) -> None:
        if lvl not in logging.__level_dict:
            return
        logging.__lvl = logging.__level_dict[lvl]
