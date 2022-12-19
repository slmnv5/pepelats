import os
from ctypes import cdll, c_int, c_void_p, c_char_p, c_double, c_bool
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

LIB_FILE = os.path.join(ROOT_DIR, "touchscr5.so")

lib = cdll.LoadLibrary(LIB_FILE)

# Each one of the below calls is a C function call contained
lib.createTouchScreen.argtypes = [c_int]
lib.createTouchScreen.restype = c_void_p

lib.clearScreen.argtypes = [c_void_p]
lib.clearScreen.restype = c_int

lib.getCols.argtypes = [c_void_p]
lib.getCols.restype = c_int

lib.getRows.argtypes = [c_void_p]
lib.getRows.restype = c_int

lib.setRowText.argtypes = [c_void_p, c_int, c_char_p, c_int, c_int, c_int]
lib.setRowText.restype = c_int

lib.setLoop.argtypes = [c_void_p, c_double, c_double, c_bool, c_bool]
lib.setLoop.restype = c_int

lib.getClickEventWord.argtypes = [c_void_p]
lib.getClickEventWord.restype = c_char_p

lib.setLogLevel.argtypes = [c_int]
lib.setLogLevel.restype = c_int

lib.stop.argtypes = [c_void_p]
lib.start.argtypes = [c_void_p]
lib.deleteTouchScreen.argtypes = [c_void_p]


class TouchScreen:
    """Load shared library to read touch screan clicks and show looper state and menu.
    Buttons made enclosing text [in brackets]. When click on this button
    get_click_event() returns text in brakets
    """

    def __init__(self, fb_id: int):
        self.tch_scr = lib.createTouchScreen(fb_id)
        if not self.tch_scr:
            raise RuntimeError("Shared library error, cannot crate screen")

    def __del__(self):
        return lib.deleteTouchScreen(self.tch_scr)

    def _clear_screen(self) -> int:
        return lib.clearScreen(self.tch_scr)

    def _get_cols(self) -> int:
        return lib.getCols(self.tch_scr)

    def _get_rows(self) -> int:
        return lib.getRows(self.tch_scr)

    def _set_row_text(self, row: int, text: str, r: int, g: int, b: int) -> int:
        return lib.setRowText(self.tch_scr, row, text.encode('utf-8'), r, g, b)

    def _set_loop(self, loop_sec: float, loop_pos: float, is_rec: bool, is_stop: bool) -> int:
        return lib.setLoop(self.tch_scr, loop_sec, loop_pos, is_rec, is_stop)

    def _get_click_event_word(self) -> str:
        bytes_arr = lib.getClickEventWord(self.tch_scr)
        return bytes_arr.decode('utf-8')

    def _delete_screen(self) -> None:
        lib.deleteTouchScreen(self.tch_scr)

    @staticmethod
    def _set_log_level(lvl: int) -> int:
        return lib.setLogLevel(lvl)


if __name__ == "__main__":
    def test1():
        x = TouchScreen(1)
        text: str = "Menu: [button 1] is first\n new line [button 2]\n no buttons on this line\n [button 3] "
        x._set_row_text(0, text, 100, 100, 100)
        while True:
            ss: str = x._get_click_event_word()
            assert ss.startswith('button')
            print(f"Got click: {ss}")
