import pyaudio
import time
import sys
import wave

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = RATE

class ChildeVoice(object):
    """docstring for ChildeVoice"""
    def __init__(self, arg):
        super(ChildeVoice, self).__init__()
        self.arg = arg
        

if __name__=="__main__":
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )
    print("Recording...")
    buffer = b""
    for i in range(3):
        buffer += stream.read(CHUNK)
    p.terminate()
    with open("test.pcm", "wb") as f:
        f.write(buffer)
    wf = wave.open(f"test.wav",'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(buffer)
    wf.close()
    print(len(buffer))

