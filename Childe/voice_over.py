import os
from Childe.config import Config
from playsound import playsound
from datetime import datetime, timedelta


voice_dir = Config["voice_resource_dir"]

voice_resource_map = {
    "Morning": "VO Tartaglia Good Morning.wav",
    "Night": "VO Tartaglia Good Night.wav",
    "After_dinner": "VO Tartaglia Good Evening.wav",
    "No_picky": "VO Tartaglia Least Favorite Food.wav",
    "Good_food": "VO Tartaglia Favorite Food.wav",
    "Comrade": "Comrade.wav",
    "Urge": "VO_Tartaglia_Joining_Party_03.wav",
    "Birthday": "VO Tartaglia Birthday.wav",
    "Diluc_Needs": "VO Diluc About Us - Needs.wav",
    "After_dinner": "VO Tartaglia Good Evening.wav",
}

class ChildVoiceOver(object):
    """docstring for ChildVoiceOver"""
    def __init__(self, voice_dir):
        super(ChildVoiceOver, self).__init__()
        self.voice_dir = voice_dir
        self.last_special_day = datetime.now() - timedelta(days=1)

    def play(self, label):
        playsound(os.path.join(self.voice_dir, voice_resource_map[label]))

    # def special_day_first_time(self, month, day):
    #     cur_time = datetime.now()
    #     if cur_time.month != month or cur_time.day != day:
    #         return False
    #     if self.last_special_day.month == cur_time.mouth and self.last_special_day.day == cur_time.day:
    #         return False
    #     self.last_special_day = cur_time
    #     return True

    # def greet(self):
    #     """
    #     Not take time zone into account yet.
    #     To be beautified.
    #     """
    #     if self.special_day_first_time(5, 8):
    #         self.play("Birthday")

    #     now_hour = datetime.now().hour
    #     if 6 <= now_hour < 11:
    #         self.play("Morning")
    #     elif 11 <= now_hour < 17:
    #         self.play("Comrade")
    #         self.play("Urge")
    #     elif 17 <= now_hour < 19:
    #         self.play("After_dinner")
    #     else:
    #         self.play("Comrade")
    #         self.play("Urge")

voice_over = ChildVoiceOver(voice_dir=voice_dir)

