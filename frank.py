from pippi import dsp, wavetables, tune, oscs, interpolation
import random

sr = 44.1
numlayers = 20

speeds = []
degrees = [1,3,5,6,9]
scale = tune.major

for i, d in enumerate(degrees):
    register = d // (len(scale) + 1)
    scale_index = scale[(d-1) % len(scale)]
    ratio = tune.terry[scale_index]
    speeds += [ (ratio[0] / ratio[1]) * 2**register ]

def makelayer(speeds):
    snd = dsp.read('harps/harp_006.wav')
    length = int(60 * 1000 * sr) * 2
    out = dsp.buffer(length=1)
    speed = random.choice(speeds) * random.choice([0.125, 0.25, 0.5, 1])
    s = snd.speed(speed)
    panpos = random.random()
    pulselength = int(random.triangular(1, 80) * sr)
    numpulses = length // pulselength
    tablesize = numpulses // 100
    ptable = interpolation.linear([ random.random() for _ in range(tablesize) ], numpulses)
    ftable = wavetables.window('line', numpulses)

    print('rendering speed: %s pan: %s len: %s num: %s' % (speed, panpos, pulselength, numpulses))
    osc = oscs.Osc(wavetable='tri')

    for i in range(numpulses-1):

        start = ptable[i] * len(s) - pulselength
        bit1 = s.cut(start if start > 0 else 0, pulselength)

        #bit2 = osc.play(length=pulselength, freq=100 * (ftable[i] + 1), amp=0.5)
        #bit1 = bit1 * bit2

        bit1 = bit1.env('sine')

        out.dub(bit1.pan(panpos) * 0.5, i * (pulselength//2))

    print('done      speed: %s pan: %s len: %s num: %s' % (speed, panpos, pulselength, numpulses))

    return out

layers = dsp.pool(makelayer, [(speeds,) for _ in range(numlayers)])

out = dsp.buffer(length=1)
for layer in layers:
    out.dub(layer, 0)
print(len(layers), len(out))
out.write('frank.wav')
