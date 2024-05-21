## MIDI drum

MIDI drum sends MIDI messages to external drum machine to synchronize it with the looper, change drum volume
and program

MIDI messages sent are:

* [] - sent after 1st loop recorded and BPM calculated. Sets BPM on external drum.
* _bar_msg - sent at start of each bar. Used to synchronize external drum
* _volume_msg - set volume using VOLUME parameter.
* _stop_msg - stop drum. There is no start message, instead use _bar_msg.
* _prog_msg - program change using PROG parameter.


### MIDI port

Each INI configuration has section "MIDI" and option "midi_out". This is MIDI port name (or part of full name) that is
used to send messages. If port is not available (device is not connected) so called "FakeMidiOut" port is used that logs
few messages in the log file.
You can see to what port MIDI drum is connected and if the port is open as described in other document.

### INI file substitution

Standard feature of INI allows to use substitution to save on typing.
Example is below when *bmp_drums* and *bpm_effects* substitute for long python expressions:
~~~


