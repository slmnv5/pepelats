## MIDI drum

MIDI drum sends MIDI messages to external drum machine to synchronize it with the looper, change drum volume
and program (aka pattern)
Two examples for hardware drum and IOS application drum are:

* [Hardware drum](./../config/drum/midi/Valeton.ini)
* [Ipad drum](./../config/drum/midi/IpadDrum.ini)

There are few elements used in the INI configuration file: messages, parameters, methods, python expressions and INI
file substitutions -- all explained below.

### Message names

Messages are listed in the section "MESSAGES" where options are message names. Valid messages are:

* _bpm_msg - sent when the 1-st loop is recorded and BPM is calculated. Used to set BPM on external drum.
* _bar_msg - sent at start of each bar. Used to synchronize external drum.
* _volume_msg - set volume
* _prog_msg - set external drum program or pattern
* _stop_msg - stop drum. There is no start message, instead it uses _bar_msg
* _progs_list - list of programs available on external drum. If not specified, GM standard is used: [0, 1, 2, ... 127]

### Message parameters

Messages may include parameters that are substituted when the message is sent.

* BPM - beats per minute. To calculate quarter note duration in milliseconds use: round(60 / BPM * 1000)
* COUNT - bar count since the start.
* VOLUME - external MIDI device volume.
* PROG - index of MIDI program from the **_progs_list**. Some IOS drums have limited pattern list, or you may use
  only few selected programs, this is when **_progs_list** is needed.

### Only method is shown below

FILL_BYTES - used to pass big number in a sys-ex message. Converts number into list of MIDI bytes:
Example: FILL_BYTES(123.49, 5) == [0, 0, 1, 2, 3 ] -- converts 123.49 into list of 5 bytes
To pass decimal part use python expression, ex: FILL_BYTES(123.49 * 100, 5) == [1, 2, 3, 4, 9]

### Python expressions

Message may include valid python expressions:

- \[0x90, 11, 12\] if COUNT == 0 else \[0x90, 111, 112\]
- \[0xCO, random.choice(\[0, 1, 2, 3\])\]
- \[0xF0, 0x5A\] + FILL_BYTES(BMP * 100, 7) + \[0xF7\]

### MIDI port

Each INI configuration has section "MIDI" and option "midi_out". This is MIDI port name (or part of full name) that is
used to send messages. If port is not available (device is not connected) so called "FakeMidiOut" port is used that logs
few messages in the log file.
You can see to what port MIDI drum is connected and if the port is open as described in other document.

### INI file substitution

Standard feature of INI allows to use substitution to save on typing.
Example is below when *bmp_drums* and *bpm_effects* substitute for long python expressions:

bpm_drum : [0xB0, 74 if BPM < 127.5 else 73, round(BPM) if BPM < 127.5 else (round(BPM) - 128)]
bpm_effects : [0xB0, 71 if BPM < 127.5 else 70, round(BPM) if BPM < 127.5 else (round(BPM) - 128)]
_bpm_msg : [%(bpm_drum)s, %(bpm_effects)s]
 

