from pippi import dsp, tune
from hcj import keys, fx, drums

kick = dsp.read('snds/kick.wav').data
hat = dsp.read('snds/hat.wav').data
snare = dsp.read('snds/snare.wav').data

bpm = 100
numbars = 8 * 4 * 4
barlength = 6
beat = dsp.bpm2frames(bpm)

# rhodes chord sequence
numchords = numbars

out = ''

# start with ran chord
# each time mutate by moving up or down the scale by a step
# each time between one and two voices move

chord = [ dsp.randint(1, 15) for _ in range(4) ]

def nextChord(last):
    degs = dsp.randshuffle(last)[:dsp.randint(1,2)]
    for deg in degs:
        newdeg = deg + dsp.randchoose([-1,1])
        if newdeg == 0:
            newdeg = 1
        #elif newdeg > 15:
        #    newdeg = 15

        last[last.index(deg)] = newdeg

    return last

kickp = 'x   '
snarep = '  x '
hatp = 'xx'

def makeHat(length, i, amp):
    h = dsp.fill(hat, length, silence=True)
    return h

def makeKick(length, i, amp):
    k = dsp.fill(kick, length, silence=True)
    return k

def makeSnare(length, i, amp):
    s = dsp.cut(snare, 0, dsp.randint(dsp.mstf(40), dsp.flen(snare)))
    s = dsp.alias(s, dsp.randint(4, 12))
    s = dsp.taper(s)
    s = dsp.fill(s, length, silence=True)
    s = dsp.amp(s, dsp.rand(2,4))
    return s

commontone = dsp.randchoose(tune.fromdegrees(chord, octave=1, root='c'))
commontone = dsp.randint(1, 9)

for b in range(numbars):
    if b % 4 == 0:
        chord = [ dsp.randint(1, 15) for _ in range(4) ]

    layers = []

    length = beat * dsp.randchoose([2, 3, 4, 6]) 
    for freq in tune.fromdegrees(chord, octave=2, root='c'):
        #freq = freq * 2**dsp.randint(0,3)
        amp = dsp.rand(0.25, 0.75)
        layer = keys.rhodes(length, freq, amp)
        layer = dsp.pan(layer, dsp.rand())
        layers += [ layer ]

    layers = dsp.mix(layers)
    ctf = tune.fromdegrees([ commontone ], octave=2, root='c')[0]
    drone = dsp.mix([ keys.pulsar(ctf, dsp.flen(layers), amp=0.3) for _ in range(4) ])

    chord = nextChord(chord)

    if b % 2 == 0:
        commontone = commontone + dsp.randchoose([-1,1])
        if commontone == 0:
            commontone = 1

    layers = dsp.split(layers, beat / 3)
    layers = dsp.randshuffle(layers)
    layers = ''.join(layers)

    drone = dsp.split(drone, beat)
    drone = dsp.randshuffle(drone)
    drone = ''.join(drone)

    #hats = dsp.fill(dsp.fill(hat, beat / 4), dsp.flen(layers))
    #kicks = dsp.fill(kick, dsp.flen(layers), silence=True)

    hats = drums.parsebeat(hatp, 8, beat, dsp.flen(layers), makeHat, 12)
    kicks = drums.parsebeat(kickp, 4, beat, dsp.flen(layers), makeKick, 0)
    snares = drums.parsebeat(snarep, 8, beat, dsp.flen(layers), makeSnare, 0)

    #dr = dsp.mix([ hats, kicks, snares ])
    dr = dsp.mix([ kicks, snares ])
    d = dsp.split(dr, beat / 8)
    d = dsp.randshuffle(d)
    #print len(d)
    #d = dsp.packet_shuffle(d, dsp.randint(2, 4))
    #print len(d)
    d = [ dd * dsp.randint(1, 2) for dd in d ]
    d = ''.join(d)
    d = dsp.fill(dsp.mix([d, dr]), dsp.flen(layers))

    d = dsp.amp(d, 3)

    layers = dsp.mix([ layers, d, drone ])

    ost = keys.rhodes(beat, tune.ntf('c', octave=4), 0.6)
    ost = dsp.env(ost, 'phasor')
    numosts = dsp.flen(layers) / dsp.flen(ost)
    ost = ''.join([ dsp.alias(ost) for _ in range(numosts) ]) 
    layers = dsp.mix([ layers, ost ])

    out += layers

dsp.write(out, 'out')
