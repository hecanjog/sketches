from pippi import dsp, oscs
import math

scale = [
    1, 
    math.sqrt(5) * 0.5,
    math.sqrt(6) * 0.5, 
    math.sqrt(7) * 0.5, 
    math.sqrt(2), 
    math.sqrt(9) * 0.5, 
    math.sqrt(10) * 0.5, 
    math.sqrt(11) * 0.5, 
    math.sqrt(3), 
    math.sqrt(13) * 0.5, 
    math.sqrt(14) * 0.5, 
    math.sqrt(15) * 0.5, 
    2, 
]


out = dsp.buffer()
osc = oscs.Osc()
osc.amp = 0.5
length = 44100//10
pos = 0

for freq in scale * 8:
    osc.freq = freq * 330
    note = osc.play(length)
    note = note.env('phasor')
    out.dub(note, pos)
    pos += int(length * 0.8)

out.write('howdoesit.wav')
