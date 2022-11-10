import os

if os.name == "posix":
    from mixer._alsamixer import AlsaMixer as Mixer
else:
    from mixer._mockedmixer import MockedMixer as Mixer
