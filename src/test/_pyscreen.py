import logging
import os
import time
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from textwrap import wrap
from threading import Event, Thread
from typing import Dict

from mvc.menucontrol import MenuControl, MenuLoader
from utils.msgprocessor import MsgProcessor
from utils.utilconfig import LEVEL_DEBUG


def test2():
    text = "[AAAAAAA] BBB CCC DDD EEE [FFFFFF] GGG " * 5
    lines = wrap(text, COLS)
    for line in lines:
        logging.debug(line)


test2()
