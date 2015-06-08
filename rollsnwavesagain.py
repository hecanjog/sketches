from pippi import dsp, tune
from hcj import keys, fx, drums

kick = dsp.read('snds/kick.wav').data
bigkick = dsp.read('snds/kick606.wav').data
snare = dsp.read('snds/snare.wav').data
snare = dsp.amp(snare, 4)
snare = dsp.env(snare, 'phasor')

snarex = dsp.split(snare, 0, 1)

changes = [
    [3,6,9],
    [3,7,9],
    [3,5,9],
]

# tempo path
def tempoPath(nsegs):
    maxms = dsp.rand(80, 400)
    minms = maxms / dsp.rand(2, 10)
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

def parseBeat(pattern, lengths, callback):
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
    h = dsp.bln(length / 4, 8000, 12000)
    h = dsp.env(h, 'phasor')
    h = dsp.fill(h, length, silence=True)

    return h

def makeKick(length, i):
    return dsp.taper(dsp.fill(bigkick, length, silence=True), 40)

def makeSnare(length, i):
    s = dsp.transpose(snare, dsp.rand(0.9, 1.1))
    if dsp.rand() > 0.5:
        s = dsp.mix([s, dsp.bln(length, 1000, 6000) ])

    s = dsp.fill(s, length, silence=True)

    return dsp.taper(s, 40)

def makeStab(length, i):
    chord = tune.fromdegrees([1,4,5,8], octave=3, root='e')
    stab = rhodesChord(length, chord, dsp.rand(0.5, 0.75))
    stab = dsp.taper(stab, 40)
    stab = dsp.fill(stab, length, silence=True)

    return stab

def splitSeg(seg):
    subseg = []
    for s in seg:
        if dsp.rand() > 0.5:
            hs = s / 2
            rs = s - hs
            subseg += [ hs, rs ]
        else:
            subseg += [ s ]

    assert sum(subseg) == sum(seg)

    return subseg

out = ''
changeindex = 0
segs = tempoPath(5)

for segi, seg in enumerate(segs): 
    print 'Rendering section %s' % (segi + 1)

    # kicks
    bar_length = dsp.randint(4, 13)
    num_pulses = dsp.randint(1, bar_length / 2)
    pattern = dsp.eu(bar_length, num_pulses)

    kicks = parseBeat(pattern, seg, makeKick)

    # snares
    bar_length = dsp.randint(6, 13)
    num_pulses = dsp.randint(1, bar_length / 2)
    pattern = dsp.eu(bar_length, num_pulses)
    pattern = dsp.rotate(pattern, dsp.randint(1,3))
    subseg = splitSeg(seg)

    snares = parseBeat(pattern, subseg, makeSnare)


    # hats
    bar_length = dsp.randint(6, 13)
    num_pulses = dsp.randint(bar_length / 2, bar_length)
    pattern = dsp.eu(bar_length, num_pulses)
    subseg = splitSeg(seg)

    hats = parseBeat(pattern, subseg, makeHat)


    # stabs
    bar_length = dsp.randint(4, 13)
    num_pulses = dsp.randint(1, bar_length)
    pattern = dsp.eu(bar_length, num_pulses)
    pattern = dsp.rotate(pattern, vary=True)

    stabs = parseBeat(pattern, seg, makeStab)
    
    # pulses
    pulses = ''
    for i, length in enumerate(seg):
        chord = tune.fromdegrees([1,4,5,8], octave=2, root='e')
        pulse = rhodesChord(length, chord, dsp.rand(0.5, 0.75)) 
        pulse = dsp.mix([ pulse, kick ])
        pulse = dsp.taper(pulse, 40)
        pulse = dsp.fill(pulse, length, silence=True)

        pulses += pulse

    section = dsp.mix([ kicks, snares, stabs, hats, pulses ])

    long_chord = rhodesChord(sum(seg), tune.fromdegrees(changes[changeindex % len(changes)], octave=dsp.randint(2,4), root='e'), dsp.rand(0.6, 0.75))
    long_chord = dsp.fill(long_chord, sum(seg))

    """
    numbeats = len(seg)
    glitch_chord = rhodesChord(sum(seg), tune.fromdegrees(changes[changeindex % len(changes)], octave=3, root='e'), dsp.rand(0.6, 0.75))
    glitch_chord = dsp.split(glitch_chord, dsp.flen(section) / numbeats)
    glitch_chord = [ dsp.amp(dsp.alias(gc), dsp.rand(0.5, 2)) for gc in glitch_chord ]
    glitch_chord = dsp.randshuffle(glitch_chord)
    glitch_chord = ''.join(glitch_chord)
    """

    changeindex = changeindex + 1

    section = dsp.mix([ section, long_chord ])

    out += section


dsp.write(out, 'rollyagain')
