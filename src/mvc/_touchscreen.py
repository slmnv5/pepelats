import os
from ctypes import cdll, c_int, c_void_p, c_char_p, c_double, c_bool

from utils.config import ROOT_DIR

LIB_FILE = os.path.join(ROOT_DIR, "touchscr5.so")

lib = cdll.LoadLibrary(LIB_FILE)

# Each one of the below calls is a C function call contained
lib.createTouchScreen.restype = c_void_p

lib.setText.argtypes = [c_void_p, c_char_p]
lib.setText.restype = c_int

lib.setLoop.argtypes = [c_void_p, c_double, c_double, c_bool, c_bool]
lib.setLoop.restype = c_int

lib.getClickEvent.argtypes = [c_void_p]
lib.getClickEvent.restype = c_char_p

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

    def __init__(self):
        self.tch_scr = lib.createTouchScreen()

    def __del__(self):
        return lib.deleteTouchScreen(self.tch_scr)

    def _set_text(self, text: str) -> int:
        return lib.setText(self.tch_scr, text.encode('utf-8'))

    def _set_loop(self, loop_sec: float, loop_pos: float, is_rec: bool, is_stop: bool) -> int:
        return lib.setLoop(self.tch_scr, loop_sec, loop_pos, is_rec, is_stop)

    def _get_click_event(self) -> str:
        bytes_arr = lib.getClickEvent(self.tch_scr)
        return bytes_arr.decode('utf-8')

    def _delete_screen(self) -> None:
        lib.deleteTouchScreen(self.tch_scr)

    @staticmethod
    def _set_log_level(lvl: int) -> int:
        return lib.setLogLevel(lvl)


if __name__ == "__main__":
    def test1():
        x = TouchScreen()
        x._set_text("Menu: [button 1] is first\n new line [button 2]\n no buttons on this line\n [button 3] ")
        while True:
            ss: str = x._get_click_event()
            assert ss.startswith('button')
            print(f"Got click: {ss}")
