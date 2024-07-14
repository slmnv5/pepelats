import os

from utils.utillog import MyLog

try:
    SCR_COLS, SCR_ROWS = os.get_terminal_size()
except OSError:
    SCR_COLS, SCR_ROWS = 30, 10  # if running inside python IDE

MyLog().info(f"Text screen size: cols={SCR_COLS} rows={SCR_ROWS}")
