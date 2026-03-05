from flask import Flask, Response, render_template
import numpy as np
import time
import struct

app = Flask(__name__)

SR = 22050
CHUNK = 1024

chords = [
    [220.0, 261.63, 329.63],
    [196.0, 246.94, 329.63],
    [174.61, 220.0, 261.63],
]

current_chord = 0
last_change = time.time()
phases = np.zeros(6)


def oscillator(freq, phase, frames):
    increment = 2*np.pi*freq/SR
    t = phase + increment*np.arange(frames)
    new_phase = (phase + increment*frames)%(2*np.pi)
    return np.sin(t), new_phase


def wav_header():
    datasize = 2000000000
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        datasize + 36,
        b'WAVE',
        b'fmt ',
        16,
        1,
        1,
        SR,
        SR * 2,
        2,
        16,
        b'data',
        datasize
    )
    return header


def generate_audio():
    global current_chord,last_change,phases

    yield wav_header()

    while True:

        if time.time()-last_change > 8:
            current_chord = (current_chord+1)%len(chords)
            last_change = time.time()

        chord = chords[current_chord]
        signal = np.zeros(CHUNK)

        for i,f in enumerate(chord):
            wave,phases[i] = oscillator(f,phases[i],CHUNK)
            signal += 0.06*wave

        bass,phases[3] = oscillator(chord[0]/2,phases[3],CHUNK)
        signal += 0.08*bass

        shimmer,phases[4] = oscillator(chord[1]*2,phases[4],CHUNK)
        signal += 0.02*shimmer

        signal += 0.003*np.random.normal(0,1,CHUNK)

        signal = np.clip(signal, -1, 1)

        pcm = (signal * 32767).astype(np.int16)

        yield pcm.tobytes()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/music")
def music():
    return Response(generate_audio(), mimetype="audio/wav")


app.run()