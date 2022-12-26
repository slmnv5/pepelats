import rtmidi.midiutil


def test_1():
    import logging

    inp = rtmidi.midiutil.open_midioutput()
    logging.debug(str(inp))
