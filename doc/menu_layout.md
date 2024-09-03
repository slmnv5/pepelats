## Menu layout

MIDI controller is coupled with **menu layout** to translates notes into looper commands.

Default layout is in directory: [6-4-menu](../config/menu/6-4-menu)
Directory name for layout have to start with two digits (ex. 6-4-...). These digits define number of buttons (MIDI
notes) used by MIDI controller and number of song parts  
As an example there is alternative layout using fewer buttons in directory : [4-2-menu](../config/menu/4-2-menu)

In every layout directory there is configuration INI file:

* [config.ini](../config/menu/6-4-menu/config.ini) -- defines MIDI notes and keyboard keys

There is navigation INI file, these commands work in all views.

* [navigate.ini](../config/menu/6-4-menu/navigate.ini) -- control navigation between views

There are 4 view INI files, commands are active only when the view is selected.

* [play.ini](../config/menu/6-4-menu/play.ini) -- playing and recording of song parts and loops
* [song.ini](../config/menu/6-4-menu/song.ini) -- saving and loading of songs
* [drum.ini](../config/menu/6-4-menu/drum.ini) -- drum configuration and parameters
* [serv.ini](../config/menu/6-4-menu/serv.ini) -- restart and other service functions

Each view may have several sections that provide different options. As an example play view has section [play.0]
to work with song parts and [play.1] to work with loops inside one part

### Controller configuration

In config.ini file there are 2 options in MIDI section:

[MIDI]

keyboard_keys -- N keys on computer keyboard, used only if MIDI controller is missing

keyboard_notes -- N notes of MIDI foot controller pedal. Note velocity must be > 10

### Menu hints

In each view top row shows drum type and beats per minute.  
Just below it there are hints for available commands.

For example in the song view hints are:

~~~
A1 go_up -- one tap on button A select previous song in llist
B1 go_dn -- one tap on button B select next song in list
B2 load -- two taps on button B load selected song
BH delete -- tap and hold of button B delete selected song
~~~



