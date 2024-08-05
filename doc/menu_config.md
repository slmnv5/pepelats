## Menu configuration

As mentioned before MIDI controller is coupled with **menu configuration files** to translates notes into looper
commands.

Default configuration is [6-4-menu](../config/menu/6-4-menu)

There are 5 views each with its own menu in default configuration (6X4) 6 buttons, 4 song parts:

* [navigate.ini](../config/menu/6-4-menu/navigate.ini) -- control navigation between views shown below:
* [play.ini](../config/menu/6-4-menu/play.ini) -- playing and recording of song parts and loops
* [song.ini](../config/menu/6-4-menu/song.ini) -- saving and loading of songs
* [drum.ini](../config/menu/6-4-menu/drum.ini) -- drum configuration and parameters
* [serv.ini](../config/menu/6-4-menu/serv.ini) -- restart and other service functions

### Controller configuration

One configuartion file sets MIDI note and computerer keyboard keys used by application:

* [config.ini](../config/menu/6-4-menu/serv.ini) -- restart and other service functions

There are 2 options in MIDI section:

[MIDI]

keyboard_keys -- 6 keys on computer keyboard if MIDI controller is missing

keyboard_notes -- 6 notes of MIDI foot controller pedal. Note velocity must be > 10

As an example there is alternative configuration using fewer buttons in directory : [4-2-menu](../config/menu/4-2-menu)

### Informationon screen

In each view top row shows drum type and beats per minute. Just below it there are hints for available commands.

For example in the song view there is list of songs with selected song in green. Commands hints are:

~~~
A1 go_up -- one tap on button A will scroll the song llist up
B1 go_dn -- one tap on button B will scroll the song list down
B2 load -- two taps on button B will load song
BH delete -- tap and hold of button B will delete selected song
~~~



