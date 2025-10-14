## Menu layout

Menu layout translates MIDI notes into looper commands.

The layout used is defined in local configuration file [local.ini](../local.ini).
If this file is missing menu layout it is taken from standard configuration file
[main.ini](../main.ini).
These files define input MIDI port name(s), number of buttons, MIDI notes (or CC) these buttons send and typing
keyboard keys that may be used when MIDI controller is missing.

The menu layout is found in directory: [menu](../config/menu), there are 3 INI files:

* [play.ini](../config/menu/play.ini) -- view for playing and recording of song parts and loops
* [song.ini](../config/menu/song.ini) -- view for managing songs and drums
* [serv.ini](../config/menu/serv.ini) -- view for restart and other service functions

Each view may have several sections that provide different options and MIDI commands. As an example play view has
section [play.0] to work with song parts and [play.1] to work with loops inside one part

### Controller configuration

In local.ini file there are 2 options in MIDI section:  
keyboard_keys -- N keys on computer keyboard, used only if MIDI controller is missing
keyboard_notes -- N notes of MIDI foot controller pedal. Note velocity must be > 10

### Menu hints

In each view top row shows drum type and beats per minute.  
Just below it there are hints for available commands.

For example in the Service_1 view hints are:

~~~
A1-next -- one tap on button A - select next song in list
AH-prev -- one tap and hold - select previous song in list
B2-load -- two taps on button B - load selected song
BH-delete -- one tap and hold of button B - delete selected song
~~~



