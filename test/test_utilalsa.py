import logging

import sounddevice as sd


def test_1():
    logging.debug("=========================")
    logging.debug(sd.query_devices())
    logging.debug("=========================")

    logging.debug("=========================")
    logging.debug(sd.query_devices(sd.default.device[0]))
    logging.debug(sd.query_devices(sd.default.device[1]))
    logging.debug("=========================")


test()
