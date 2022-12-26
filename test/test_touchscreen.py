import logging

# noinspection PyProtectedMember
import mvc._touchscreen


# noinspection PyPep8
def test_1():
    x = mvc._touchscreen.TouchScreen(1)
    text: str = "Menu: [button 1] is first\n new line [button 2]\n no buttons on this line\n [button 3] "
    x._set_row_text(0, text, 100, 100, 100)
    while True:
        ss: str = x._get_click_event_word()
        assert ss.startswith('button')
        logging.debug(f"Got click: {ss}")
