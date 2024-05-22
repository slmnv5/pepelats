## Menu configuration

MIDI controller is coupled with **menu configuration files** which translate notes to looper commands.
Menu configurations are described here [menu_config](./img/menu%20_config.png)
Each configuration directory has 5 files:

* navigate.ini -- control navigation between 4 views of the looper shown below:
    * play.ini -- main view that controls playing and recording of song parts and loops
    * song.ini -- view that control saving and loading of saved songs
    * drum.ini -- view that controls drum configuration and parameters
    * serv.ini -- view that controls restart and other service functions

The screen of each view shows hints for available button mappings. For example in song view there is list of songs
with selected song in green:

![song_view](img/song_view.png)

Top row shows drum type and configuration name, beats per minute
Below are hints for available button mappings:

~~~
A1 go_up -- one tap on button A will scroll the song llist up
B1 go_dn -- one tap on button B will scroll the song list down
B2 load -- two taps on button B will load song
BH delete -- tap and hold of button B will delete song
~~~



