# Song

Song is collection of recorded song parts along with specific drum type and configuration. If there are undo/redo
actions and loop modifications (muting, reversing) they are saved, as well as drum parameters.

Saved songs are found in user's home, in subdirectory ~/save_song. Song names look like "02.Disco", "08.Blues". Names
include unique number from 00 to 99 and suffix showing drum configuration name.

In service_1 view songs may be saved, loaded, deleted, initialized and assigned drum configuration (Disco, Blues, ...).


## Stopping song

[Service_1 view](../config/menu/song.ini) also has commands for stopping song instantly or at the end of the longest
loop in the currently playing song part  

