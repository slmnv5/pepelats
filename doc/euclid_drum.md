## Euclid drum

**Euclid drum** rhythms use four parameters: steps, beats, offset and accent.

- Steps - length (or period) of the pattern.
- Beats - how many drum hits there is in one period.
- Offset - position of first beat, other beats are spread most evenly over all steps.
- Accent - how many steps have accented sound, e.g. if accent = 3 each 3rd step is accented if there is a beat.

Euclid drum allows creating very long non-repeating patterns using very simple notation. As an example 208 step long
sequence for bass drum (bd) and snare drum (sd).
Using traditional patterns this would take half a page of space and will be prone to errors.

~~~
bd : 16, 4, 0, 0
sd : 13, 8, 0, 0
~~~

This drum type also uses WAV sound samples as described [here](./pattern_drum.md)
It is implemented in IOS application 'Ruismaker' which has user manual explaining it all.
