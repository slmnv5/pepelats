## MIDI drum

**MIDI drum** sends MIDI messages to external drum machine to synchronize it with the looper, change drum volume,
program number, etc. External drum machine must implement these messages.
Alternatively more processing of custom MIDI messages may be done with IOS application (e.g. MidiFire) to convert them
to usable form.   
As example here is script file for MidiFire [midi_fire_scene.txt](../etc/txt/midi_fire_scene.txt) that controls drum
machine on IOS.

Each set of MIDI messages along with the OUT port name saved in configuration file. There are two predefined
configurations:
[ValetonGP-100.ini](../config/drum/midi/ValetonGP-100.ini)
[MidiFire.ini](../config/drum/midi/MidiFire.ini)

### MIDI messages:

Six messages to control MIDI device, each may contain variables:

* bpm_msg -- sent once when BMP is defined (when loading song, recording 1st loop)
* bar_msg -- sent at start of each bar, there is no start message, **bar_msg** is used
* stop_msg -- stop external drum
* volume_msg -- volume (ex. CC #7 from 0 to 127)
* prog_list -- list of program external device is using, =[0] if it is missing
* prog_msg -- select a program from **prog_list**

### MIDI messages:

Six variables used in messages (all upper case names):

* BPM -- beats per minute, ex. 123.56
* BPM_LIST = [0, 1, 2, 3, 5, 6] if BPM = 0123.56
* DUR_LIST = [2, 3, 7, 8] if bar duration = 2378 milliseconds (2.378 seconds)
* PROG -- program number in the prog_list, value is: 0 =< PROG < length of prog_list
* VOLUME -- volume from 0.0 to 1.0
* COUNT -- count of bars since the latest start

### MIDI out port for MIDI drum

Each drum configuration file has section "MIDI" and option "midi_out". This is MIDI port name (or part of the
name) used to send MIDI drum messages. If port is not available (device is not connected) a "fake" MIDI out port
is used which only logs first 20 MIDI messages  
After MIDI drum is connected you need to reload song or set drum configuration file so that looper will connect to
this port 



