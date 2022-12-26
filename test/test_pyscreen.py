import logging
# noinspection PyProtectedMember
from textwrap import wrap

# noinspection PyProtectedMember
from mvc._pyscreen import COLS


def test_1():
    text = "[AAAAAAA] BBB CCC DDD EEE [FFFFFF] GGG " * 5
    lines = wrap(text, COLS)
    for line in lines:
        logging.debug(line)



