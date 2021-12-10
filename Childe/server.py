import numpy as np
import pyaudio
import threading
from datetime import datetime, timedelta
import os, sys
# from python_speech_features import mfcc
from Childe.voice2txt import BaiduVoiceAPI
from Childe.wakeup import WakeUpWord
from Childe.utils import save_wav_from_np, rand_name




class Recorder(threading.Thread):

    def __init__(self, queue, record_config, chunk_size=8000):
        super(Recorder, self).__init__()
        self.CHUNK = chunk_size
        self.queue = queue
        self.config = record_config

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(**self.config)
        while 1:
            chunk = stream.read(self.CHUNK)
            self.queue.put(chunk)
            # print("put chunk")


class Detector(threading.Thread):

    def __init__(self, queue, api_config, wakeup_window=5, chunk_size=8000, threshold=2000):
        super(Detector, self).__init__()
        self.queue = queue
        self.wakeup_window = wakeup_window
        self.chunk_size = chunk_size
        self.threshold = threshold
        self.prevs = [np.zeros(chunk_size, dtype=np.int16) for i in range(wakeup_window - 1)]
        self.voice_api = BaiduVoiceAPI(api_config)
        self.wakeup_model = WakeUpWord(model_exists=True)

    def run(self):
        while 1:
            chunk = self.queue.get()
            np_chunk = np.frombuffer(chunk, dtype=np.int16)
            self.prevs.append(np_chunk)
            # print("get chunk")
            if max(np_chunk) > self.threshold and self.wakeup():
                raise ValueError
                self.wakeup_response()
                self.handle_commands()
                self.finish_response()
            self.prevs = self.prevs[1:]

    def collect_hostile_samples(self, dir_path):
        while 1:
            chunk = self.queue.get()
            np_chunk = np.frombuffer(chunk, dtype=np.int16)
            self.prevs.append(np_chunk)
            if max(np_chunk) > self.threshold and self.wakeup():
                print("GOTCHA")
                self.dump_audio(os.path.join(dir_path, f"{rand_name()}.wav"))
            self.prevs = self.prevs[1:]

    def handle_commands(self):
        counter = 7
        raw_data = b""
        while counter:
            chunk = queue.get()
            np_chunk = np.frombuffer(chunk, dtype=np.int16)
            if max(np_chunk) > self.threshold and self.identification(np_chunk):
                raw_data += chunk
            elif raw_data:
                # 这里之后改成异步
                sentences = self.voice_api.voice2txt(raw_data=raw_data)
                for sentence in sentences:
                    self.executeCommand(sentence)
                raw_data = b""
                counter -= 1
        self.prevs = [np.zeros(self.chunk_size, dtype=np.int16) for i in range(wakeup_window - 1)]

    def request_command(self, command):
        print(command)

    def wakeup(self):
        x = np.concatenate(self.prevs)
        return self.wakeup_model.predict(x.astype(np.float32))

    def identification(self, chunks):
        return True

    def wakeup_response(self):
        print("Hi comrade!")

    def finish_response(self):
        print("Done.")

    def dump_audio(self, path):
        x = np.concatenate(self.prevs)
        save_wav_from_np(x, path)