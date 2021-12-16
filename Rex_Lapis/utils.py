import requests
import json
from Rex_Lapis.config import voice2txt_config
from datetime import datetime, timedelta
from Rex_Lapis.logger import logger

class APIAccess(object):
    """docstring for APIAccess"""
    def __init__(self, config):
        super(APIAccess, self).__init__()
        self.config = config
        self.getToken()

    def getToken(self):
        r = requests.post(self.config["token_url"], params=self.config["api_key"])
        r = json.loads(r.text)
        self.token = r[self.config["token_key"]]
        self.tokenExpireTime = datetime.utcnow() + timedelta(**self.config["token_duration"])


class BaiduVoiceAPI(APIAccess):

    def __init__(self, config):
        super(BaiduVoiceAPI, self).__init__(config)
        self.v2t_url = self.config["v2t_api_url"]
        self.t2v_url = self.config["t2v_api_url"]

        self.response_audio_type = "audio/pcm;rate=16000"

        # Not configurable yet. Bad practice
        self.cuid = "b19dcc00798b9b9422bf0e13f147ef7676ab3a18e9efc65e66f0d82aab851c74"

    def voice2txt(self, raw_data, language="EN"):
        dev_pid = 1737 if not language or language == "0" or language == "EN" else 1537
        params = {
            "params": {
                "cuid": self.cuid,
                "dev_pid": dev_pid,
                "token": self.token,
            },
            "headers": {
                "Content-Type": "audio/pcm;rate=16000"
                # "Content-Type": "audio/wav;rate=16000"
            },
            "data": raw_data
        }

        try:
            if self.tokenExpireTime < datetime.utcnow():
                self.getToken()
            r = requests.post(self.v2t_url, **params)
            r = json.loads(r.text)
            assert r["err_msg"] == "success."
            return r["result"]
        except:
            return [] 

    def txt2voice(self, tex):

        data = {
            "tex": tex,
            "lan": "zh",
            "cuid": "b19dcc00798b9b9422bf0e13f147ef7676ab3a18e9efc65e66f0d82aab851c74",
            "ctp": 1,
            "tok": self.token,
            # 发音人选择, 基础音库：0为度小美，1为度小宇，3为度逍遥，4为度丫丫，
            # 精品音库：5为度小娇，103为度米朵，106为度博文，110为度小童，111为度小萌，默认为度小美 
            "per": 106,
            # pcm-16k
            "aue": 4,

            # # 语速，取值0-15，默认为5中语速
            # SPD = 5
            # # 音调，取值0-15，默认为5中语调
            # PIT = 5
            # # 音量，取值0-9，默认为5中音量
            # VOL = 5
            # # 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
        }

        if self.tokenExpireTime < datetime.utcnow():
            self.getToken()
        r = requests.post(self.t2v_url, data=data)

        if r.headers["Content-Type"] == "application/json":
            json_response = json.loads(r.text)
            logger.log(level="ERROR", message=f"T2V API Access failure: {json_response['err_msg']} ({tex})")
            return b""
        elif r.headers["Content-Type"] == "audio/basic;codec=pcm;rate=16000;channel=1":
            return r.content
        else:
            logger.log(level="ERROR", message=f"Unexpected failure in utils.py txt2voice.")
            return b""



API_maps = {
    "BaiduVoiceAPI": BaiduVoiceAPI
}

voice_api = API_maps[voice2txt_config.pop("api")](voice2txt_config)