import rtmidi.midiutil


def test():
    import logging

    inp = rtmidi.midiutil.open_midioutput()
    logging.debug(str(inp))


test()
