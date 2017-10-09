from pippi import dsp, oscs, wavetables, tune, rhythm
import random

def makenote(length, freq, lfo=0.5, amp=0.05, factor=10):
    wavetable = 'tri'
    wtsize = 4096
    ftable = [ v * factor + 1 for v in wavetables.wavetable('random', wtsize) ]
    factors = [ v * ftable[i] for i, v in enumerate(wavetables.wavetable('sine', wtsize)) ]
    osc = oscs.Fold(wavetable, factors, freq, lfo, amp)
    return osc.play(length)

def makebass(length, freq, lfo=0.5, amp=0.05, factor=10):
    wavetable = 'square'
    wtsize = 4096
    ftable = [ v * factor + 1 for v in wavetables.wavetable('random', wtsize) ]
    factors = [ v * ftable[i] for i, v in enumerate(wavetables.wavetable('sine', wtsize)) ]
    osc = oscs.Fold(wavetable, factors, freq, lfo, amp)
    return osc.play(length)


chords = []
for c in 'I I6 IV6 IV69 I I6 IV6 IV69 iii vi ii7 V11'.split(' '):
    chords += [ c ] * 4

out = dsp.buffer(length=1)
length = 44100 // 4

lenmult = 4

hat = dsp.read('manys/many_300.wav')
snare = dsp.read('manys/many_400.wav')
kick = dsp.read('manys/many_500.wav')
kick = kick.speed(0.8)

def makesynths():
    out = dsp.buffer(length=1)
    beat = length // 2
    numbeats = 16 * 8 * lenmult
    pat = rhythm.topattern('x..x....')
    onsets = rhythm.onsets(pat, beat, numbeats)

    for i, pos in enumerate(onsets):
        chord = chords[i % len(chords)]
        freqs = tune.chord(chord)

        for freq in freqs:
            lfo = random.random() * i * 0.5 
            note = makenote(random.randint(length // 4, length * 3), freq * 0.25 * 2**random.randint(0, 4), lfo, factor=random.randint(1, 10))
            note = note.env('phasor')
            note = note.pan(random.random())
            out.dub(note * 0.65, pos)

    return out

out.dub(makesynths(), 0)


def makearps():
    out = dsp.buffer(length=1)
    beat = length // 2
    numbeats = 16 * 8 * lenmult
    pat = rhythm.topattern('xxxxxxxx')
    onsets = rhythm.onsets(pat, beat, numbeats)

    osc = oscs.Osc('tri')

    for i, pos in enumerate(onsets):
        chord = chords[i//4 % len(chords)]
        freqs = tune.chord(chord)
        freq = freqs[i % len(freqs)]
        amp = random.triangular(0.1, 0.2)
        pw = random.triangular(0.15, 1)

        note = osc.play(beat, freq * 2, amp * 0.25, pw)
        note = note.env('phasor')
        out.dub(note, pos)

    return out

out.dub(makearps(), 0)


def makeblips():
    out = dsp.buffer(length=1)
    beat = length // 2
    numbeats = 16 * 8 * lenmult
    pat = rhythm.topattern('x..x..x.')
    onsets = rhythm.onsets(pat, beat, numbeats)

    for i, pos in enumerate(onsets):
        chord = chords[i*2 % len(chords)]
        freqs = tune.chord(chord)

        lfo = random.random() * 2
        freq = freqs[0] * 0.5
        if i % 8 == 0:
            freq *= 2

        note = makenote(length, freq, lfo, factor=random.randint(1, 10))
        note = note.env('phasor')
        out.dub(note * 2, pos)

    return out

out.dub(makeblips(), 0)

def makehats():
    out = dsp.buffer(length=1)
    beat = length // 2
    numbeats = 16 * 8 * lenmult
    pat = rhythm.topattern('x xxx xx')
    onsets = rhythm.onsets(pat, beat, numbeats)
    onsets = rhythm.swing(onsets, 0.5, beat)

    for i, pos in enumerate(onsets):
        out.dub(hat.speed(random.triangular(1.5, 2)) * random.triangular(0.35, 0.45), pos)

    return out

out.dub(makehats(), 0)

def makesnares():
    out = dsp.buffer(length=1)
    beat = length
    numbeats = 16 * 4 * lenmult
    pat = rhythm.topattern('..x...x...x...xx..x...x...x....x')
    onsets = rhythm.onsets(pat, beat, numbeats)

    for i, pos in enumerate(onsets):
        if random.random() > 0.75:
            s = dsp.buffer(length=1)
            p = rhythm.curve(numbeats=random.randint(4, 10), wintype='random', length=beat*random.randint(2,3))
            for o in p:
                s.dub(snare.speed(random.triangular(0.9,1.1)) * random.random(), o)

            out.dub(s, pos)

        out.dub(snare, pos)

    return out

out.dub(makesnares(), 0)

def makekicks():
    out = dsp.buffer(length=1)
    beat = length
    numbeats = 16 * 4 * lenmult
    pat = rhythm.topattern('x...')
    onsets = rhythm.onsets(pat, beat, numbeats)

    for i, pos in enumerate(onsets):
        out.dub(kick.speed(random.triangular(0.8,1)) * 1.4, pos)

    return out

out.dub(makekicks(), 0)

out.write('foldy.wav')
