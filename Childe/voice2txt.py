from requests import get, post
import json
from datetime import datetime, timedelta
# from Childe.config import Config
from Childe.utils import APIAccess


class BaiduVoiceAPI(APIAccess):

    def voice2txt(self, raw_data, language="EN"):
        if not language or language == "0" or language == "EN":
            dev_pid = 1737
        else:
            dev_pid = 1537
        params = {
            "params": {
                "cuid": "b19dcc00798b9b9422bf0e13f147ef7676ab3a18e9efc65e66f0d82aab851c74",
                "dev_pid": dev_pid,
                "token": self.token,
            },
            "headers": {
                "Content-Type": "audio/pcm;rate=16000"
                # "Content-Type": "audio/wav;rate=16000"
            },
            "data": raw_data
        }
        r = post(self.config["api_url"], **params)
        r = json.loads(r.text)
        if r["err_msg"] == "success.":
            return r["result"]
        return []     

if __name__ == "__main__":

    from config import Config
    config = Config["voice2txt"]

    api_access = BaiduVoiceAPI(config)
    with open("test.pcm", "rb") as f:
        raw_data = f.read()
    r = api_access.voice2txt(language="EN", raw_data=raw_data)
    if r:
        print(r)
