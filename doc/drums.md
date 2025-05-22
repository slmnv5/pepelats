Drums

Looper has embedded drum machine that may use different drums:

- [Stile drum](style_drum) - using text patterns - with drum names steps, accents
- [Euclid drum](euclid_drum) - using Euclid algorithm to generate long non repeating rythms
- [MIDI drum](midi_drum) - using INI configurateon to send MID commands (stop, start of loop, etc)
- [Loop drum](loop_drum) - using the first loop as drum

### Drum fills

There are two drum intensity levels for drums - normal and break/fill.
For Style drum, Euclid drum patterns are split into 2 groups based on name -- if pattern name contans string "brk"
it is a break pattern and used only to play drum breaks.

For Loop drum - the last recorded loop in the first part of song is treated as fill.

For MIDI drum fill may be configured in INI file by sending specific MIDI command.

### Drum swing

Style drum and Euclid drum have a swing parameter.
