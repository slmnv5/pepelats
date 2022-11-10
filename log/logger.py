import logging
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

level = "WARN"
if "--debug" in sys.argv:
    level = "DEBUG"
if "--info" in sys.argv:
    level = "INFO"

logging.basicConfig(level=os.getenv("DEBUG_LEVEL", level), filename=Path(ROOT_DIR, 'log.log'), filemode='w')
LOGR = logging.getLogger()
fm = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
LOGR.handlers[0].setFormatter(fm)
LOGR.propagate = False

LOGR.info(f"=======>Starting looper's log {LOGR.handlers}")
