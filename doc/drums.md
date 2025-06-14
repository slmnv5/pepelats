Drums

Looper has embedded drum machine that may use different drums:

- [Style drum](style_drum) - using text patterns - with drum names steps, accents
- [MIDI drum](midi_drum) - using INI configuration to send MID commands (stop, start of loop, etc.)
- [Loop drum](loop_drum) - using the first loop as drum

### Drum break/fill

There are two drum intensity levels for drums - normal and break/fill.
For Style drum patterns are split into 2 groups based on name -- if pattern name contains string "brk"
it is a break pattern and used only to play drum breaks.

For Loop drum - the last recorded loop in the first part of song is treated as break.

For MIDI drum break/fill may be configured in INI file by sending specific MIDI command.

### Drum swing

Style drum has a swing parameter that can be adjusted and saved with the song.
