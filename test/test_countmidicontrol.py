import logging

from mvc import CountMidiControl
from mvc.menucontrol import MenuLoader
from utils.utilalsa import get_midi_in


# noinspection PyProtectedMember


def test_1():
    from multiprocessing.dummy import Pipe

    logging.getLogger().setLevel(logging.INFO)
    recv_fake, send_fake = Pipe()
    in_port = get_midi_in()

    menu_loader = MenuLoader("config/menu", "play", "0")
    m_ctrl = CountMidiControl(in_port, send_fake, menu_loader)
    try:
        m_ctrl.monitor()  # will throw EOF when all mesages processed
    except EOFError:
        pass



