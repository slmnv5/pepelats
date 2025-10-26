## Style drum

**Style drum** is using text patterns specific for musical style and sample WAV files to produce drum accompaniment.

There are plenty of musical styles in directory: [config/drum/style](./../config/drum/style)
Example: [Pop.ini](../config/drum/style/Pop.ini)

WAV sound samples are stored in [config/drum/samples](./../config/drum/wav)

### Drum patterns

Drum pattern example is shown below. Each pattern is inside one INI section. Number of steps is equal to the longest
drum length.

~~~
[Pop1A 4/4]  
;...1234567890123456  
ac: ....!.......!...  
ch: !.!.!.!.!.!.!.!.  
sd: ....!.!.....!...  
bd: !.......!.....!.  
~~~

* ac -- shows accents for each step
* bd, sd -- are drum names
* "." -- silence on a step
* "!" -- drum hit on a step

### Drum names
Drum names used in pattern INI file and WAV file names are the same (ex. sd.wav, bd.wav):

* ac: Accent - increases drum hit volume on specific step
* bd: Bass drum
* sd: Snare Drum
* lt: Low tom
* mt: Medium tom
* ht: High tom
* ch: Closed hi-hat
* oh: Open hi-hat
* cy: Cymbal
* rs: Rim shot
* cp: Clap
* cb: Cowbell

