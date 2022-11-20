import logging
import os
import time
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from multiprocessing.connection import Pipe
from threading import Thread, Event
from typing import Dict

from utils import MsgProcessor, SD_RATE
from utils import RedrawScreen

if os.name == "posix":
    NEWL: str = ''
    UPDATES_PER_LOOP: float = 16
else:
    NEWL: str = '\n'
    UPDATES_PER_LOOP: float = 1

try:
    COLS, ROWS = os.get_terminal_size()
except OSError:
    COLS, ROWS = 30, 10

logging.error(f"Screen size: cols={COLS} rows={ROWS}")

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
    if line[0] == "*":
        if is_rec:
            return ScrColors['r'] + line + ScrColors['end']
        else:
            return ScrColors['g'] + line + ScrColors['end']
    elif line[0] == "~":
        return ScrColors['y'] + line + ScrColors['end']
    else:
        return line


class ScreenView(MsgProcessor):

    def __init__(self, recv_conn: Connection):
        MsgProcessor.__init__(self, recv_conn, None)
        self.__play_event: Event = Event()
        self.__header = "".center(COLS)
        self.__descr_lines: int = 0

        self.__loop_len = self.__idx = self.__delta = 1000000
        self.__sleep_time: float = 1
        Thread(target=self.__update_progress, name="update_progress", daemon=True).start()

    def _send_redraw(self, infodic: Dict) -> None:
        logging.debug("Get redraw: " + str(infodic))
        if "header" in infodic:
            self.__header = infodic["header"].center(COLS)

        if "description" in infodic:
            self.__update_description(infodic["description"])

        if "redraw" in infodic:
            self.__update_loops(infodic["redraw"])

    def __update_description(self, description: str) -> None:
        if description:
            extra_chars = len(description) % COLS
            if extra_chars:
                description = description + '.' * (COLS - extra_chars)
            self.__descr_lines = len(description) // COLS
            print(f"\033[2;1H{description}")
        else:
            self.__descr_lines = 0

    def __update_loops(self, redraw: RedrawScreen) -> None:
        logging.debug(f"Updating screen: {redraw}")
        if redraw.is_stop:
            self.__play_event.clear()
        else:
            self.__play_event.set()
            self.__idx = redraw.idx
            self.__loop_len = redraw.loop_len
            self.__delta = redraw.loop_len / UPDATES_PER_LOOP
            if os.name == "posix":
                self.__sleep_time = self.__delta / SD_RATE

        lines = redraw.content.split('\n')
        left_lines: int = max(0, ROWS - 1 - self.__descr_lines)
        lines = lines[:left_lines]
        lines_count = len(lines)
        tmp = ""
        for k in range(lines_count):
            line = lines[k][:COLS].ljust(COLS)
            line = get_with_color(line, redraw.is_rec)
            tmp += line + NEWL
        left_lines = max(0, ROWS - 1 - self.__descr_lines - lines_count)
        tmp += ' ' * COLS * left_lines + NEWL
        print(f"\033[{2 + self.__descr_lines};1H{tmp}", end='', flush=True)

    def __update_progress(self):
        while True:
            self.__play_event.wait()
            time.sleep(self.__sleep_time)
            self.__idx += self.__delta
            self.__idx %= self.__loop_len
            pos = round(self.__idx / self.__loop_len * COLS)
            line = '\x1b[7m' + self.__header[:pos] + '\x1b[0m' + self.__header[pos:]
            # all starts at 1, 1
            print(f"\033[1;1H{line}")


if __name__ == "__main__":
    def test():
        recv_view, send_view = Pipe(False)  # screen update messages

        scr_view = ScreenView(recv_view)
        Thread(target=scr_view.process_messages, daemon=True).start()
        time.sleep(8)
