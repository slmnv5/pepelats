import logging
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from mvc.menucontrol import MenuControl, MenuLoader



def test():
    from utils.utilport import ChargedMidiPort
    from multiprocessing.dummy.connection import Pipe
    recv_fake, send_fake = Pipe()
    in_port = ChargedMidiPort()
    in_port.charge({0.1: (60, 100), 0.2: (-60, 0), 1.2: (62, 1)})
    menu_loader = MenuLoader("config/menu", "play", "0")
    m_ctrl = MidiControl(in_port, send_fake, menu_loader)
    try:
        m_ctrl.monitor()  # will throw EOF when all mesages processed
    except EOFError:
        pass

    send_fake.close()
    while recv_fake.poll():
        msg = recv_fake.recv(timeout=0.001)
        logging.debug(msg)


test()
