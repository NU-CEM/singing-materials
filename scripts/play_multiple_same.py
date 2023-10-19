import sounddevice
import numpy
import time

SAMPLE_RATE = 44100

def callback(outdata: numpy.ndarray, frames: int, time, status) -> None:
    """writes sound output to 'outdata' from sound_queue."""
    result = None
    print(frequencies)
    for frequency in frequencies:
        t = (start_index + numpy.arange(frames)) / SAMPLE_RATE
        t = t.reshape(-1, 1)

        wave = numpy.sin(2 * numpy.pi * frequency * t)

        if result is None:
            result = wave
        else:
            result += wave

        frequencies[frequency] += frames

    if result is None:
        result = numpy.arange(frames) / SAMPLE_RATE
        result = result.reshape(-1, 1)

    outdata[:] = result

def stream(freqs,length):
    """streams overlaid sinewaves for set length of time.
    frequencies in hz, time in s."""
    global frequencies 
    frequencies = freqs
    stream = sounddevice.OutputStream(channels=2, blocksize=SAMPLE_RATE, 
            samplerate=SAMPLE_RATE, callback=callback)
    stream.start()
    time.sleep(length)

if __name__ == "___main__":
    stream([440,220],3)
