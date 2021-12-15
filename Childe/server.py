import numpy as np
import pyaudio
import requests
from datetime import datetime, timedelta
import os
import sys
import time
import json
import threading
from Childe.wakeup import WakeUpWord
from Childe.utils import rand_name, save_wav
from Childe.config import Config
from Childe.logger import logger
from Childe.voice_over import voice_over

device_name = Config["device"]
salt = Config["salt"]
wakeup_url = Config["wakeup_url"]
request_url = Config["request_url"]
tmp_dir = Config["tmp_dir"]

p = pyaudio.PyAudio()

class ChildeServer(object):

    def __init__(self):
        super(ChildeServer, self).__init__()
        # self.queue = Queue(maxsize=Config["wakeup_queue_size"])
        self.wakeup_window = Config["wakeup_window"]
        self.chunk_size = Config["voice_record"]["frames_per_buffer"]
        self.threshold = Config["voice_filter"]["threshold"]
        self.prevs = b"\x00" * self.wakeup_window
        self.wakeup_model = WakeUpWord(model_exists=True)

        self.condition = threading.Condition()
        self.condition_command = threading.Condition()

        self.instream = p.open(**Config["voice_record"], stream_callback=self.fill_queue)

        self.input_ready = False
        self.command_finished = False

        self.voice_labels = []

    # 最外层永真循环
    #   等待可能的 wakeup
    #       如果是真的 wakup
    #           关闭之前的流 ( 关闭 fill_queue callback )
    #           开启 command 的 callback，用来处理 command
    #           等待 command 处理结束
    #           关闭 command 流
    #           开启 fill_queue callback
    def run(self):
        while 1:
            with self.condition:
                while not self.input_ready:
                    # As long as the fill_queue callback is pending, this wait has the chance to be awaken.
                    # The problem is spurious wakeup
                    self.condition.wait()
                if self.wakeup():
                    logger.log(level="DEBUG", message=f"Wake Up.")
                    self.instream.close()

                    # Awaken, play the greeting audio
                    for voice_label in self.voice_labels:
                        voice_over.play(voice_label)

                    self.prevs = b""
                    self.counter = 3
                    while self.counter:
                        self.instream = p.open(**Config["voice_record"], stream_callback=self.command_callback)
                        with self.condition_command:
                            while not self.command_finished:
                                self.condition_command.wait()
                            self.command_finished = False
                            self.instream.close()
                            if self.prevs:
                                raw_response = self.request_Morax(url=request_url, raw_data=self.prevs)
                                json_response = json.loads(raw_response)
                                print(json_response["message"])

                                self.prevs = b""
                                counter = 3
                            else:
                                self.counter -= 1
                    self.session.close()
                    self.instream = p.open(**Config["voice_record"], stream_callback=self.fill_queue)
                    self.prevs = b"\x00" * self.wakeup_window
                self.input_ready = False

    """
    If the wakeup window is 3s, it would be better to read 1s each time, and check the wakeup at callback.
    When activated, use another callback to collect commands audio.

    Not sure if it is a good idea...... As the recording will wait the callback function.
    No idea whether can it works. Try it later.

    After some test, it is not a good idea. Callback should be quick.
    """
    def fill_queue(self, in_data, frame_count, time_info, status):
        if frame_count != self.chunk_size:
            logger.log(level="CRITICAL", message=f"Stream_callback get a inconsistent chunk. frame_count: {frame_count}")
            sys.exit()

        # print(datetime.utcnow())
        # time.sleep(1)
        self.prevs += in_data
        self.prevs = self.prevs[-self.wakeup_window:]

        np_chunk = np.frombuffer(in_data, dtype=np.int16)
        if max(np_chunk) > self.threshold:
            with self.condition:
                self.input_ready = True
                self.condition.notify()

        # The callback must return a tuple (out_data, flag)
        # Reference: https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.PyAudio.open
        return None, pyaudio.paContinue


    # This callback is sort of slower. It requires to talk to the Rex_Lapis.
    # But it is desired. I do not want the recording when it is analyzing.
    def command_callback(self, in_data, frame_count, time_info, status):

        if frame_count != self.chunk_size:
            logger.log(level="CRITICAL", message=f"Stream_callback get a inconsistent chunk. frame_count: {frame_count}")
            sys.exit()

        np_chunk = np.frombuffer(in_data, dtype=np.int16)
        if max(np_chunk) > self.threshold:
            self.prevs += in_data
            return None, pyaudio.paContinue

        with self.condition_command:
            self.command_finished = True
            self.condition_command.notify()

        # When output=True and out_data does not contain at least frame_count frames, paComplete is assumed for flag.
        # So that you can not set the output flag as True
        return None, pyaudio.paComplete

    def request_Morax(self, url, raw_data, auth=False):

        if auth:
            headers = {
                "Authorization": f"X-KeeperAuth {device_name};{salt}",
            }
        else:
            headers = {}
        try:
            r = self.session.post(url, data=raw_data, headers=headers)
        except:
            logger.log(level="ERROR", message="Request failed.")
            return b""
        if r.status_code != 200:
            logger.log(level="ERROR", message=f"Request error. Status code: {r.status_code}")
            return b""
        if r.headers.get("Content-Type", "") == "application/json":
            return json.loads(r.text)
        elif r.headers.get("Content-Type", "") == "audio/pcm;rate=16000":
            return r.content
        else:
            logger.log(level="ERROR", message=f"Unexpected Content-Type.")
            return b""
 

    def wakeup(self):
        # starttime = datetime.utcnow()
        x = np.frombuffer(self.prevs, dtype=np.int16)
        if not self.wakeup_model.predict(x.astype(np.float32)):
            # print("Start", starttime, "End", datetime.utcnow())
            return False
        self.session = requests.Session()
        # Invocation of request_Morax will only return dict when success, otherwise b""
        response = self.request_Morax(url=wakeup_url, raw_data=self.prevs, auth=True)
        if not response:
            return False
        if not response.get("wakeup", False):
            file_name = f"{rand_name()}.wav"
            # logger.log(level="INFO", message=f"Probably misfire detected. {json.loads(raw_response).get('message', '')}")
            logger.log(level="INFO", message=f"Probably misfire detected. Saving as {file_name}.")
            save_wav(x, os.path.join(tmp_dir, file_name), filt=False)
            return False

        self.voice_labels = response["voice_labels"]
        return True

    def request_Command(self):
        raw_response = self.request_Morax(url=request_url, raw_data=self.prevs)
        if not raw_response:
            self.voice_labels = ["Remote_Failure"]
        if type(raw_response) == bytes:
            pass
        # dict
        else:
            pass





