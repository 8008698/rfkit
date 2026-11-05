"""NepDate राशिफल भिडियो audio generator.
numpy र scipy भए पूर्ण धुन (flute + tanpura + temple bells) सिन्थेसाइज गर्छ।
नभए Python को wave मोड्युलबाट आधारभूत अडियो बनाउँछ ताकि ffmpeg ले भिडियो जोड्न सकोस्।"""
import math, os, struct, wave

try:
    import numpy as np
    from scipy.io import wavfile
    from scipy.signal import butter, sosfilt, fftconvolve
    HAS_NUMPY_SCIPY = True
except ImportError:
    HAS_NUMPY_SCIPY = False

SR = 44100

def make_numpy(T, ev, seed=1):
    rng = np.random.default_rng(seed)
    N = int(T * SR)
    L = np.zeros(N)

    def add(x, t0, g=1.0):
        i = int(t0 * SR)
        j = min(N, i + len(x))
        if i < N and j > i:
            L[i:j] += g * x[:j - i]

    t = lambda d: np.arange(int(d * SR)) / SR

    def tanp(f, d=3.2):
        x = t(d)
        y = np.zeros_like(x)
        for h in range(1, 15):
            a = (1 / h) * (1 + 1.6 * np.exp(-((h - 6) / 2.2) ** 2))
            y += a * np.sin(2 * np.pi * f * h * x + rng.random() * 6.28) * np.exp(-x * (0.7 + 0.18 * h))
        return y * np.minimum(1, x * 200) * 0.14

    def bell(f, d=2.2, g=1.0, low=False):
        x = t(d)
        y = np.zeros_like(x)
        parts = [(1, 1, 1.0), (2.71, .5, .7), (5.15, .28, .45), (8.2, .12, .3)] if low else [(1, 1, 1.0), (2.76, .5, .6), (5.4, .25, .4), (8.93, .12, .25)]
        for r, a, dc in parts:
            y += a * np.sin(2 * np.pi * f * r * x) * np.exp(-x * dc * (2.2 if not low else 1.1))
        return y * np.minimum(1, x * 300) * 0.2 * g

    def flute(f, d, g=1.0):
        x = t(d)
        vib = 0.006 * np.sin(2 * np.pi * 5.2 * x) * np.minimum(1, x * 2)
        ph = 2 * np.pi * np.cumsum(f * (1 + vib)) / SR
        y = np.sin(ph) + .28 * np.sin(2 * ph) + .1 * np.sin(3 * ph)
        env = np.minimum(1, x / .12) * np.minimum(1, (d - x) / .3)
        n = rng.standard_normal(len(x))
        sos = butter(2, [2000, 6000], "bp", fs=SR, output="sos")
        return (y * env * 0.2 + sosfilt(sos, n) * env * 0.012) * g

    def whoosh(d):
        x = t(d)
        n = rng.standard_normal(len(x))
        env = np.sin(np.pi * x / d) ** 2
        sos = butter(2, [500, 5000], "bp", fs=SR, output="sos")
        return sosfilt(sos, n) * env * 0.35 * np.linspace(.4, 1, len(x))

    pat = [(110.0, 0), (146.83, .6), (146.83, 1.2), (73.42, 1.8)]
    tt = 0.0
    while tt < T - 1:
        for f, o in pat:
            add(tanp(f), tt + o)
        tt += 2.4

    x = t(T)
    pad = np.zeros(N)
    for f, a in ((146.83, .05), (220, .045), (293.66, .03), (370, .02)):
        pad += a * np.sin(2 * np.pi * f * x) * (0.7 + 0.3 * np.sin(2 * np.pi * (0.11 + f / 3000) * x))
    L += pad * np.minimum(1, x / 3)

    for w in ev.get("whoosh", []):
        add(whoosh(1.2), max(0, w), 0.8)
    for h in ev.get("hits", []):
        add(bell(220, 5, 1.1, True), h)
        add(bell(587.33, 3, .7), h + .05)
    for q in ev.get("pops", []):
        add(bell(1174.7, 2, .6), q)
        add(bell(880, 2.5, .5), q + .1)
    for i, s_ in enumerate(ev.get("stars", [])):
        add(bell([1318.5, 1568, 1760, 2093, 2349][i % 5], 1.6, .5), s_)
    for s_ in ev.get("cards", []):
        add(whoosh(.5), s_ - .05, .3)
        add(bell(987.8, 1.5, .3), s_ + .2)

    O = ev.get("out")
    if O:
        add(bell(293.66, 5, 1.3, True), O + .5)
        add(bell(880, 4, .7), O + .6)
        add(bell(1174.7, 3, .5), O + 1.2)
    else:
        O = T - 1.0

    ph = [(440, 1.2), (493.88, .6), (440, .6), (370, 1.2), (329.63, .8), (293.66, 1.6), (0, .4),
          (370, .8), (440, .8), (493.88, 1.2), (587.33, 1.8), (493.88, .6), (440, 1.0), (370, 1.0),
          (329.63, .8), (293.66, 2.0), (0, .5)]
    tm = ev.get("intro", 0) + 3.0
    i = 0
    while tm < O - .2:
        f, d = ph[i % len(ph)]
        i += 1
        if f:
            add(flute(f, min(d, O - tm)), tm)
        tm += d

    for s in np.arange(1.0, max(5.0, ev.get("intro", 0) - 2), .5):
        add(bell(float(rng.choice([1174.7, 1318.5, 1568, 1760])), 1.2, .18), float(s))

    ir = rng.standard_normal(int(1.8 * SR)) * np.exp(-np.arange(int(1.8 * SR)) / SR / .55)
    ir /= np.abs(ir).sum() / 6
    y = L * .8 + fftconvolve(L, ir)[:N] * .35

    fade = np.ones(N)
    fo = int(1.2 * SR)
    fade[-fo:] = np.linspace(1, 0, fo)
    y *= fade
    max_val = np.max(np.abs(y))
    if max_val > 0:
        y /= max_val / 0.88
    R = np.concatenate([np.zeros(int(.012 * SR)), y])[:N]
    return np.column_stack([y, R])

def make_fallback(T):
    """numpy/scipy नहुँदा मानक wave मोड्युलबाट मद्धिम ambient धुन बनाउँछ।"""
    num_samples = int(T * SR)
    frames = bytearray()
    for i in range(num_samples):
        t = i / SR
        # Gentle acoustic drone on D (146.83 Hz) and A (220 Hz)
        fade_in = min(1.0, t / 1.5)
        fade_out = min(1.0, (T - t) / 1.5)
        env = fade_in * fade_out
        s1 = 0.08 * math.sin(2 * math.pi * 146.83 * t)
        s2 = 0.05 * math.sin(2 * math.pi * 220.0 * t)
        v = (s1 + s2) * env
        val = int(v * 32767)
        frames.extend(struct.pack("<hh", val, val))
    return frames

def write(path, T, ev, seed=1):
    if HAS_NUMPY_SCIPY:
        data = make_numpy(T, ev, seed)
        wavfile.write(path, SR, (data * 32767).astype(np.int16))
    else:
        print("सूचना: numpy/scipy भेटिएन — आधारभूत ambient धुन प्रयोग भयो।")
        frames = make_fallback(T)
        with wave.open(path, "w") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(SR)
            wav.writeframes(frames)
