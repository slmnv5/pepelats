import logging
import sys

level = "WARN"
if "--debug" in sys.argv:
    level = "DEBUG"
if "--info" in sys.argv:
    level = "INFO"

logging.basicConfig(stream=sys.stderr, level=level, format='%(asctime)s %(levelname)s %(message)s')
logging.error('>>> Starting looper <<<')
LOGGER = logging.getLogger()
# fm = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# logging.handlers[0].setFormatter(fm)
# logging.propagate = False
