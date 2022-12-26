import logging
from ctypes import cdll, c_int, c_void_p, c_char_p, c_double, c_bool

from mvc._touchscreen import TouchScreen
from utils.utilconfig import ROOT_DIR, ConfigName

 def test1():
    x = TouchScreen(1)
    text: str = "Menu: [button 1] is first\n new line [button 2]\n no buttons on this line\n [button 3] "
    x._set_row_text(0, text, 100, 100, 100)
    while True:
        ss: str = x._get_click_event_word()
        assert ss.startswith('button')
        logging.debug(f"Got click: {ss}")
