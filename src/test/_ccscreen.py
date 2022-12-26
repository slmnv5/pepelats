import time
# noinspection PyProtectedMember
from multiprocessing.connection import Pipe
from threading import Thread

from mvc._ccscreen import CcScreen
from mvc.menucontrol import MenuLoader


def test1():
    recv_view, send_view = Pipe(False)  # screen update messages
    menu_loader = MenuLoader("config/menu", "play", "0")
    scr_view = CcScreen(recv_view, send_view, menu_loader, "1")
    Thread(target=scr_view.process_messages, daemon=True).start()
    time.sleep(8)
