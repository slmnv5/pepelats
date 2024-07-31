# Song

Song is collection of recorded song parts along with specific drum type and configuration. If there are undo/redo
actions and loop modifications (muting, reversing) they are saved, as well as drum parameters.

Song names are generated automatically using random word selections. Also, song name has suffix indication drum type (
S-Style drum, E-Euclid drum, L-Loop drum, M-Midi drum) and file extension ".sng"

Examples of song names: "last_pen.S.sng", "her_family.L.sng". Saved songs are found in directory "save_song".

Song may be saved, loaded, deleted, cleared, updated with another drum type.

Number of parts in song depends on menu configuration. Default configuration 6x4 has 4 parts. To change it another menu
configuration need to be selected.

When loading song audio samples are converted to current device settings. As an example a song may be recorded on
audio device as (mono, 44100, int16) and be loaded as (stereo, 48000, float32).  
