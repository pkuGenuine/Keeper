"""
Childe, the audio frontend.
"""
from queue import Queue
import threading, sys, os
from . import server
from . import config


def start():
    threshold = config.Config["voice_filter"]["threshold"]
    wakeup_queue_size = config.Config["wakeup_queue_size"]
    wakeup_queue = Queue(maxsize=wakeup_queue_size)
    recorder = server.Recorder(queue=wakeup_queue, record_config=config.Config["voice_record"])
    detector = server.Detector(queue=wakeup_queue, threshold=threshold, api_config=config.Config["voice2txt"])
    recorder.start()
    detector.start()
    try:
        detector.join()
        recorder.join()
    except KeyboardInterrupt:
        sys.exit()

def hostile_collect(dir_path):
    threshold = config.Config["voice_filter"]["threshold"]
    wakeup_queue_size = config.Config["wakeup_queue_size"]
    wakeup_queue = Queue(maxsize=wakeup_queue_size)
    recorder = server.Recorder(queue=wakeup_queue, record_config=config.Config["voice_record"])
    detector = server.Detector(queue=wakeup_queue, threshold=threshold, api_config=config.Config["voice2txt"])
    recorder.start()
    detector.collect_hostile_samples(dir_path)

if __name__ == "__main__":
    start()


