# Song

Song is collection of recorded song parts along with specific drum type and configuration. If there are undo/redo
actions and loop modifications (muting, reversing) they are saved, as well as drum parameters.

Song names are generated automatically using random word selections. Also, song name has suffix indication drum type (
S-Style drum, L-Loop drum, M-Midi drum) and file extension ".sng"

Examples of song names: "last_pen.S.sng", "big_family.L.sng". Saved songs are found in user's home, in subdirectory
~/save_song.

Song may be saved, loaded, deleted, initialized, updated with another drum type.

Number of parts in song depends on menu configuration. Default configuration 6x4 has 4 parts. To change it select
another menu configuration

When loading song audio samples are converted to current device settings. As an example a song may be recorded on
audio device as (mono, 44100, int16) and be loaded as (stereo, 48000, float32)

## Stopping song

[Song view](../config/menu/6-4-menu/song.ini) also has commands for stopping song instantly or at the end of the longest
loop in the currently playing song part  

