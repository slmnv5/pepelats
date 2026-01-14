#Drums

Looper has embedded drum machine that may use different drums:

- [Style drum](style_drum) - using INI configuration for text patterns - with drum names, steps, accents
- [MIDI drum](midi_drum) - using INI configuration to send MID commands (stop, start of loop, etc.)
- [Loop drum](loop_drum) - using the first song part as a drum and part's loops as drum variations

### Drum break/fill

There are two drum intensity levels for drums - normal and break/fill.
Different types of drums implement breaks as described here.

For Style drum patterns are split into 2 groups based on the name -- if pattern name contains string "brk" it is used for breaks only.

For Loop drum - depending on style a break may be 1) the last recorded loop or 2) all loops playing together.

For MIDI drum break/fill may be configured in INI file by sending specific MIDI command. This command may be program change or other command specific for your midi device.

### Drum swing

Style drum has a swing parameter that can be adjusted and saved with the song.
