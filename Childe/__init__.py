"""
Childe, the audio frontend.
"""
import sys, os
from . import server
from . import config

audio_detector = server.ChildeServer()

if __name__ == "__main__":
    audio_detector.run()


