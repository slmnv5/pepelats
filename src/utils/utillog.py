import logging
import sys

_fmt_str = "%(asctime)s;%(levelname)s;%(name)s>>>%(message)s"


def get_my_log(name: str, level: int = None) -> logging.Logger:
    logger = logging.getLogger(name)
    assert not logger.handlers
    for h in logger.handlers:
        logger.removeHandler(h)

    formatter = logging.Formatter(fmt=_fmt_str, datefmt="%Y-%m-%d %H:%M:%S")
    fname: str = "./log.txt"

    handler_file = logging.FileHandler(fname, mode='a')
    handler_file.setFormatter(formatter)

    handler_screen = logging.StreamHandler(sys.stderr)
    handler_screen.setFormatter(formatter)

    logger.addHandler(handler_screen)
    logger.addHandler(handler_file)

    if level is not None:
        pass
    elif "--debug" in sys.argv:
        level = logging.DEBUG
    elif "--info" in sys.argv:
        level = logging.INFO
    else:
        level = logging.WARNING

    logger.setLevel(level)
    return logger
