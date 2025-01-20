## Menu layout

MIDI controller is coupled with **menu layout** to translates notes into looper commands.

Default layout is in directory: [6-4-menu](../config/menu/6-3-menu)
Directory name for layout have to start with two digits (ex. 6-4-...). These digits define number of buttons (MIDI
notes) used by MIDI controller and number of song parts  
As an example there is alternative layout in directory : [6-3-menu](../config/menu/6-4-menu) with dedicated button for
recording

In the **main.ini** configuration file there is **[MIDI]** section:

* [main.ini](../main.ini) -- defines MIDI notes and keyboard keys used by controller

In the menu directory there are 5 INI files:

* [navigation.ini](../config/menu/6-3-menu/navigation.ini) -- navigation between views, commands available in all views
* [play.ini](../config/menu/6-3-menu/play.ini) -- view for playing and recording of song parts and loops
* [song.ini](../config/menu/6-3-menu/song.ini) -- view for stopping, saving and loading of songs
* [drum.ini](../config/menu/6-3-menu/drum.ini) -- view for drum configuration and parameters
* [serv.ini](../config/menu/6-3-menu/serv.ini) -- view for restart and other service functions

Each view may have several sections that provide different options. As an example play view has section [play.0]
to work with song parts and [play.1] to work with loops inside one part

### Controller configuration

In main.ini file there are 2 options in MIDI section:  
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



