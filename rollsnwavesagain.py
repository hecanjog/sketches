from pippi import dsp, tune
from hcj import keys, fx, drums

kick = dsp.read('snds/kick.wav').data
bigkick = dsp.read('snds/kick606.wav').data
snare = dsp.read('snds/snare.wav').data
snare = dsp.amp(snare, 6)
snare = dsp.env(snare, 'phasor')

snarex = dsp.split(snare, 0, 1)

key = 'a'

hatp =   'xxxx'
snarep = '..x...x...'
kickp =  'x...-.....x..x...'
pulsep = 'x..'

# tempo path
def tempoPath(nsegs):
    maxms = dsp.rand(100, 400)
    minms = dsp.rand(1, 100)
    wavetypes = ['hann', 'sine', 'vary']

    out = []

    for _ in range(nsegs):
        seglen = dsp.randint(20, 200)
        seg = dsp.wavetable(dsp.randchoose(wavetypes), seglen)

        # pull out a randomly selected subsegment of the curve
        sublen = seglen / dsp.randint(2, 5)
        segstart = dsp.randint(0, seglen - sublen)
        segend = segstart + sublen
        seg = seg[segstart:segend]

        out += [ [ dsp.mstf(abs(s) * (maxms - minms) + minms) for s in seg ] ]

    return out

def rhodesChord(length, chord, amp):
    layers = [ keys.rhodes(length, freq, amp * dsp.rand(0.25, 0.5)) for freq in chord ]
    layers = [ dsp.pan(layer, dsp.rand()) for layer in layers ]

    return dsp.mix(layers)

def parseBeat(pattern):
    out = []
    for tick in pattern:
        if tick == 'x':
            out += [ 1 ]
        else:
            out += [ 0 ]

    return out

def makeBeat(pattern, lengths, callback):
    out = ''

    for i, length in enumerate(lengths):
        # Silence or beat?
        amp = pattern[i % len(pattern)]

        if amp > 0:
            out += callback(length, i)
        else:
            out += dsp.pad('', 0, length)

    assert dsp.flen(out) == sum(lengths)

    return out

def makeHat(length, i):
    h = dsp.bln(length / 4, dsp.rand(6000, 8000), dsp.rand(9000, 16000))
    h = dsp.amp(h, dsp.rand(0.5, 1))
    h = dsp.env(h, 'phasor')
    h = dsp.fill(h, length, silence=True)

    return h

def makeKick(length, i):
    return dsp.taper(dsp.fill(dsp.mix([ bigkick, kick ]), length, silence=True), 40)

def makeSnare(length, i):
    burst = dsp.bln(length, dsp.rand(400, 800), dsp.rand(8000, 10000))
    burst = dsp.env(burst, 'phasor')
    s = dsp.mix([snare, burst])
    s = dsp.transpose(s, dsp.rand(0.9, 1.1))

    s = dsp.fill(s, length, silence=True)

    return dsp.taper(s, 40)

def makeStab(length, i):
    chord = tune.fromdegrees([ dsp.randchoose([1,4,5,8]) for _ in range(dsp.randint(2,4)) ], octave=3, root=key)
    stab = rhodesChord(length, chord, dsp.rand(0.5, 0.75))
    stab = dsp.taper(stab, 40)
    stab = dsp.fill(stab, length, silence=True)

    return stab

def makePulse(length, i):
    chord = tune.fromdegrees([ dsp.randchoose([1,4,5,8]) for _ in range(dsp.randint(2,4)) ], octave=2, root=key)
    pulse = rhodesChord(length, chord, dsp.rand(0.5, 0.75)) 
    #pulse = dsp.mix([ pulse, kick ])
    pulse = dsp.taper(pulse, 40)
    pulse = dsp.amp(pulse, dsp.rand(0.9, 1.5))
    pulse = dsp.fill(pulse, length, silence=True)

    return pulse


def splitSeg(seg, size=2, vary=False):
    def split(s, size):
        hs = s / size
        rs = s - hs
        return [ hs, rs ]

    subseg = []
    for s in seg:
        if vary:
            if dsp.rand() > 0.5:
                subseg += split(s, size)
            else:
                subseg += [ s ]
        else:
            subseg += split(s, size)

    assert sum(subseg) == sum(seg)

    return subseg

out = ''
changeindex = 0
segs = tempoPath(30)

for segi, seg in enumerate(segs): 
    print 'Rendering section %s' % (segi + 1)

    # kicks
    pattern = parseBeat(kickp)
    kicks = makeBeat(pattern, seg, makeKick)

    # snares
    pattern = parseBeat(snarep)
    subseg = splitSeg(seg, 2)
    snares = makeBeat(pattern, subseg, makeSnare)

    # hats
    pattern = parseBeat(hatp)
    subseg = splitSeg(seg, 4)
    hats = makeBeat(pattern, subseg, makeHat)


    # stabs
    bar_length = dsp.randint(4, 13)
    num_pulses = dsp.randint(1, bar_length)
    pattern = dsp.eu(bar_length, num_pulses)
    pattern = dsp.rotate(pattern, vary=True)
    subseg = splitSeg(seg, 3)

    stabs = makeBeat(pattern, subseg, makeStab)
    
    # pulses
    pattern = parseBeat(pulsep)
    pulses = makeBeat(pattern, seg, makePulse)

    section = dsp.mix([ kicks, snares, stabs, hats, pulses ])

    chord = [ dsp.randint(1, 9) for _ in range(dsp.randint(2,4)) ]
    long_chord = rhodesChord(sum(seg), tune.fromdegrees(chord, octave=dsp.randint(2,4), root=key), dsp.rand(0.6, 0.75))
    long_chord = dsp.fill(long_chord, sum(seg))

    def makeGlitch(length, i):
        g = dsp.cut(long_chord, dsp.randint(0, dsp.flen(long_chord) - length), length)
        g = dsp.alias(g)
        g = dsp.fill(g, length)

        return g

    subseg = splitSeg(seg, 2)
    glitches = makeBeat([1,1], subseg, makeGlitch)

    changeindex = changeindex + 1

    section = dsp.mix([ section, long_chord, glitches ])

    out += section


dsp.write(out, 'rollyagain')
