## MIDI drum

MIDI drum sends MIDI messages to external drum machine to synchronize it with the looper, change drum volume
and program

MIDI messages sent are:

*1) [0xF0, 0x5A, BPM_LIST, 0xF7] - sysEx message sent after 1st loop recorded and BPM calculated. Sets BPM on external
drum. BPM_LIST is 6 bytes long. For bpm=123.45 it will be filled with decimal values: [0, 1, 2, 3, 4, 5]
*2) [0xF0, 0x5B, 0xF7] - sysEx message sent at start of each bar. Used to synchronize external drum
*3) [0xB0, 8, VOL] - set volume where VOL has value from 0 to 128.
*4) [0xFC] - stop drum. There is no start message, instead 2) is used.
*4) [0xC0, PROG] - program change where PROG number from 0 to 32.

### MIDI port

**Main.ini** configuration has section "MIDI" and option "midi_out". This is MIDI port name (or part of full name) that
is used to send messages. If port is not available (device is not connected) so called "FakeMidiOut" port is used that
logs few messages in the log file.
You can see to what port MIDI drum is connected and if the port is open as described in other document.



