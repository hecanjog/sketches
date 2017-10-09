import random

from pippi import dsp

harp = dsp.read('harp1.wav')

out = dsp.silence(1)

for grain in harp.grains(100, 1000):
    grain = grain.env('blackman') * random.random()
    out.dub(grain, random.randint(0, 44100))

out.write('harpy.wav')
