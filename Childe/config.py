import pyaudio

Config = {
    "wakeup_queue_size": 2,
    "queue_size": 100,
    "voice_record": {
        "format": pyaudio.paInt16,
        "channels": 1,
        "rate": 16000,
        "frames_per_buffer": 8000,
        "input": True
    },
    "voice_filter": {
        "threshold": 2000
    },
    "voice2txt": {
        "api": "ai.baidu",
        "token_url": "https://aip.baidubce.com/oauth/2.0/token",
        "api_key": {
            "grant_type":"client_credentials", 
            "client_id":"SaubuKzLp0ZHHdoa1YDjyxBn", 
            "client_secret": "2kUpGoDWd5LHbZ79VFf4Ylpq7GveFNrh"
        },
        "token_key": "refresh_token",
        "token_duration": {
            "days": 30
        },
        "api_url": "http://vop.baidu.com/server_api"
    }
}
