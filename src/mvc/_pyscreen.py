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

if os.name == "posix":
    UPDATES_PER_LOOP: float = 16
    NEWLINE = ''
else:
    UPDATES_PER_LOOP: float = 1
    NEWLINE = '\n'

try:
    COLS, ROWS = os.get_terminal_size()
except OSError:
    COLS, ROWS = 30, 10

logging.info(f"Text screen size: cols={COLS} rows={ROWS}")

# foreground, background ends with '40m'
ScrColors: Dict[str, str] = {
    'b': '\x1b[1;30m',
    'r': '\x1b[1;31m',
    'g': '\x1b[1;32m',
    'y': '\x1b[1;33m',
    'v': '\x1b[1;34m',
    'w': '\x1b[37m',
    'end': '\x1b[0m',
    'reverse': '\x1b[7m'
}


def get_with_color(line: str, is_rec: bool) -> str:
    if not line:
        return ""
    if line[0] == "*":
        if is_rec:
            return ScrColors['r'] + line + ScrColors['end']
        else:
            return ScrColors['g'] + line + ScrColors['end']
    elif line[0] == "~":
        return ScrColors['y'] + line + ScrColors['end']
    else:
        return line


def clr_screen() -> None:
    if not LEVEL_DEBUG:
        print(f"\033[2;1H{' ' * COLS * (ROWS - 1)}", end='', flush=True)


class PyScreen(MsgProcessor, MenuControl):

    def __init__(self, recv_conn: Connection, send_conn: Connection, menu_loader: MenuLoader):
        MsgProcessor.__init__(self, recv_conn, None)
        MenuControl.__init__(self, send_conn, menu_loader)
        self.__play_event: Event = Event()
        self.__header: str = "=>Pepelats Looper<="
        self.__loop_seconds: float = 3
        self.__loop_position: float = 0
        Thread(target=self.process_messages, name="message_thread", daemon=True).start()

    def _send_redraw(self, redraw) -> None:
        logging.debug(f"Get redraw: {redraw}")
        if redraw.is_stop:
            self.__play_event.clear()
        else:
            self.__play_event.set()
            self.__loop_position = redraw.loop_position
            self.__loop_seconds = redraw.loop_seconds

        clr_screen()
        self.__header = redraw.header[:COLS].center(COLS)
        lines = wrap(redraw.text, COLS)
        k: int = 2
        for line in [x for x in lines if x]:
            print(f"\033[{k};1H{line}", end=NEWLINE)
            k += 1

        lines = redraw.content.split('\n')
        for line in lines:
            line = line[:COLS]
            line = get_with_color(line, redraw.is_rec)
            print(f"\033[{k};1H{line}", end=NEWLINE)
            k += 1
        print("", end='', flush=True)

    def monitor(self):
        while True:
            self.__play_event.wait()
            time.sleep(self.__loop_seconds / UPDATES_PER_LOOP)
            self.__loop_position += 1.0 / UPDATES_PER_LOOP
            if self.__loop_position >= 1:
                self.__loop_position -= 1

            pos = round(self.__loop_position * COLS)
            line = '\x1b[7m' + self.__header[:pos] + '\x1b[0m' + self.__header[pos:]
            # all starts at 1, 1
            print(f"\033[1;1H{line}", end='', flush=True)


if __name__ == "__main__":
    pass
