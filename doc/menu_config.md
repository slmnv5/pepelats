## Menu configuration

As mentioned before MIDI controller is coupled with **menu configuration files** to translates notes into looper
commands.
There are 5 views each with its own menu in default configuration (6X4) 6 buttons, 4 song parts:

* [navigate.ini](./../config/menu/6x4/navigate.ini) -- control navigation between views shown below:
* [play.ini](./../config/menu/6x4/play.ini) -- playing and recording of song parts and loops
* [song.ini](./../config/menu/6x4/song.ini) -- saving and loading of songs
* [drum.ini](./../config/menu/6x4/drum.ini) -- drum configuration and parameters
* [serv.ini](./../config/menu/6x4/serv.ini) -- restart and other service functions

Alternative configuration uses fewer buttons (4X2) 4-buttons, 2-song parts found in directory : [4x2](../config/menu/4x2)

In each view top row shows drum type and beats per minute. Just below it there are hints for available commands.
For example in the song view there is list of songs with selected song in green.
Commands hints are:

~~~
A1 go_up -- one tap on button A will scroll the song llist up
B1 go_dn -- one tap on button B will scroll the song list down
B2 load -- two taps on button B will load song
BH delete -- tap and hold of button B will delete selected song
~~~



