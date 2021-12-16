import os
from Childe.config import Config
from Childe.utils import save_wav, rand_name
from Childe.logger import logger
from playsound import playsound
from datetime import datetime, timedelta


voice_dir = Config["voice_resource_dir"]
fallback_voice_dir = Config["voice_fallback_dir"]


tmp_dir = Config["tmp_dir"]

voice_resource_map = {
    "Morning": "VO Tartaglia Good Morning.wav",
    "Night": "VO Tartaglia Good Night.wav",
    "AfterDinner": "VO Tartaglia Good Evening.wav",
    "NoPicky": "VO Tartaglia Least Favorite Food.wav",
    "GoodFood": "VO Tartaglia Favorite Food.wav",
    "Comrade": "Comrade.wav",
    "Urge": "VO_Tartaglia_Joining_Party_03.wav",
    "Birthday": "VO Tartaglia Birthday.wav",
    "Windy": "VO Tartaglia When It's Windy.wav",
    "Diluc_Needs": "VO Diluc About Us - Needs.wav",
    "Diluc_OK": "VO_Diluc_Opening_Treasure_Chest_02.wav",
    "Albedo_Understood": "VO_Albedo_Joining_Party_01.wav",
}

fallback_voice_resource_map = {
    "Not_Understand": "Not_Understand.wav",
    "Error": "Error.wav",
}

class CharacterVoiceOver(object):

    def __init__(self, voice_dir, resource_map):
        super(CharacterVoiceOver, self).__init__()
        self.voice_dir = voice_dir
        self.resource_map = resource_map

    def play(self, label):
        # If label not in map, simply raise Error
        playsound(os.path.join(self.voice_dir, self.resource_map[label]))


class DefaultVoice(CharacterVoiceOver):

    def __init__(self, voice_dir, tmp_dir, resource_map):
        super(DefaultVoice, self).__init__(voice_dir=voice_dir, resource_map=resource_map)
        self.tmp_dir = tmp_dir

    def play(self, label):
        if label not in self.resource_map:
            logger.log(level="ERROR", message=f"Unsupported voice label {label}.")
            label = "Error"
        playsound(os.path.join(self.voice_dir, self.resource_map[label]))

    def play_raw(self, raw_data):
        tmp_file = os.path.join(self.tmp_dir, rand_name() + ".wav")
        save_wav(raw_data=raw_data, path=tmp_file, filt=False)
        playsound(tmp_file)
        # os.system(f"rm {tmp_file}")

voice_over = CharacterVoiceOver(voice_dir=voice_dir, resource_map=voice_resource_map)
fallback_voice = DefaultVoice(voice_dir=fallback_voice_dir, tmp_dir=tmp_dir, resource_map=fallback_voice_resource_map)


