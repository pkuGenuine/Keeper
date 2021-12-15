"""
Provide base utilities to other modules.
Only support wav file with one channel and 16 depth for now.
"""

from requests import get, post
import json
from datetime import datetime, timedelta
from Childe.config import Config
from hashlib import sha1
import os
import pyaudio
from playsound import playsound
import wave
import numpy as np
import random
import time
from collections import defaultdict
import code


sample_width = 2
THRESHOLD = Config["voice_filter"]["threshold"]
CHUNK = Config["voice_record"]["frames_per_buffer"]
RATE = Config["voice_record"]["rate"]
CHANNELS = Config["voice_record"]["channels"]

p = pyaudio.PyAudio()

def drand(n=32):
    with open("/dev/random", "rb") as f:
        return f.read(n)

def rand_name(n=8):
    return sha1(drand()).digest().hex()[:n]


def record_raw(chunks=5):
    global sample_width
    p = pyaudio.PyAudio()
    stream = p.open(**Config["voice_record"])
    ret = b""
    for i in range(chunks):
        ret += stream.read(Config["voice_record"]["frames_per_buffer"])
    sample_width = p.get_sample_size(Config["voice_record"]["format"])
    p.terminate()
    return ret

def save_pcm(raw_data, path):
    np_chunk = np.frombuffer(raw_data, dtype=np.int16)
    if max(np_chunk) <= THRESHOLD:
        return
    with open(path, "wb") as f:
        f.write(raw_data)

def save_wav(raw_data, path, filt=True):
    if filt and max(np.frombuffer(raw_data, dtype=np.int16)) <= THRESHOLD:
        return
    wf = wave.open(path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(raw_data)
    wf.close()

def wav2raw(path):
    with open(path, "rb") as f:
        return f.read()[44:]


class Recorder(object):
    def __init__(self, save_path="", auto_name=True):
        if not save_path:
            save_path = os.path.join("resource", "origin_voices")
        self.save_path = save_path
        self.auto_name = auto_name
        """
        TODO:
        1. Controled record length.
        2. Add more file types.
        """
    def record(self, chunks=5, vtype="noise", ftype="wav", file_name=""):
        raw_data = record_raw(chunks=chunks)
        if self.auto_name:
            file_name = file_name + "_" + rand_name()
        if ftype != "wav":
            raise NotImplementedError
        save_wav(raw_data, os.path.join(self.save_path, vtype, f"{file_name}.wav"))


class VoiceDataEnhancer(object):
    """
    1. Record voices for trainning.
    2. Enhance Data

    Note:
    1. Only support np.int16 and np.float32 for now
    """
    def __init__(self, noise_path=""):
        super(VoiceDataEnhancer, self).__init__()
        if not noise_path:
            noise_path = os.path.join("resource", "origin_voices", "noise")
        self.noise_path = noise_path


    def dum_filter(np_chunk):
        THRESHOLD = 1000
        above_threshold = np_chunk > THRESHOLD
        indices = np.nonzero(above_threshold)
        try:
            # indices may be of zero size
            imin = np.min(indices)
        except:
            return np_chunk
        imax = np.max(indices)
        return np_chunk[imin: imax]


    def shift_chunk(self, np_chunks, chunk_filter=None):
        target_length = len(np_chunks[0])
        if not chunk_filter:
            chunk_filter = VoiceDataEnhancer.dum_filter
        return self.random_trunc_or_padding([chunk_filter(np_chunk) for np_chunk in np_chunks], target_length)


    def random_trunc_or_padding(self, np_chunks, target_length):
        ret = []
        dt = np_chunks[0].dtype
        for np_chunk in np_chunks:
            slots = len(np_chunk) - target_length
            if slots > 0:
                start_at = random.randint(0, slots)
                ret.append(np_chunk[start_at: start_at+target_length])
            elif slots == 0:
                ret.append(np_chunk)
            else:
                slots = -slots
                l_slots = random.randint(0, slots)
                r_slots = slots - l_slots
                ret.append(np.concatenate([np.zeros(l_slots, dtype=dt), np_chunk, np.zeros(r_slots, dtype=dt)]))
        return ret

    def add_noise(self, np_chunks, noise_nums=32):
        ret = []
        noise_files = list(filter(lambda x: x.endswith(".wav"), os.listdir(self.noise_path)))
        total_num = len(noise_files)
        choices = random.sample(range(total_num), noise_nums)
        noise_chunks = []
        dt = np_chunks[0].dtype
        for choice in choices:
            with open(os.path.join(self.noise_path, noise_files[choice]), "rb") as f:
                # Endian may cause trouble here...
                # Still only support wav file with one channel and 16 depth
                noise_chunk = np.frombuffer(f.read()[44:], dtype=np.int16)
                noise_chunks.append(noise_chunk)
        noise_concat_chunk = np.concatenate(noise_chunks)
        for np_chunk in np_chunks:
            target_length = len(np_chunk)
            noise_chunk = self.random_trunc_or_padding([noise_concat_chunk], target_length)[0]
            ret.append(np_chunk + (noise_chunk * 0.3).astype(dt))
        return ret


class CNNDataLoader(object):
    def __init__(self, file_sample_loader, paths, labels):
        self.samples = []
        self.labels = []
        self.total_sample = 0
        self.counts = defaultdict(int)
        for file_path, label in zip(paths, labels):
            for file in os.listdir(file_path):
                datas = file_sample_loader(os.path.join(file_path, file), label)
                count = len(datas)
                self.samples += datas
                self.labels += [label for i in range(count)]
                self.total_sample += count
                self.counts[label] += count
        print("Sample component ratio:")
        for k, v in self.counts.items():
            print(k, v/self.total_sample, f"({v})")
    def __getitem__(self, key):
        return (self.samples[key].astype(np.float32), self.labels[key])
    def __len__(self):
        return self.total_sample


