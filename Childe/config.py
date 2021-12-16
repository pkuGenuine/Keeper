import pyaudio
import os

envs = os.environ

Config = {
    # "wakeup_queue_size": 2,
    "wakeup_window": 40000,
    "queue_size": 100,
    "voice_record": {
        "format": pyaudio.paInt16,
        "channels": 1,
        "rate": 16000,
        "frames_per_buffer": 16000,
        "input": True
    },
    "voice_output": {
        "format": pyaudio.paInt16,
        "channels": 1,
        "rate": 16000,
        "frames_per_buffer": 400,
        "output": True
    },
    "voice_filter": {
        "threshold": 4000
    },
    "salt": "pi_salt_changeme",
    "wakeup_url": "http://localhost:5000/wakeup",
    "request_url": "http://localhost:5000/commands",

    # No space is allowed in device name 
    "device": "Raspberry_pi",

    "tmp_dir": "/Users/liuzhanpeng/working/Keeper/tmp",

    "voice_resource_dir": "/Users/liuzhanpeng/working/Keeper/resource/output_voices",
    "voice_fallback_dir": "/Users/liuzhanpeng/working/Keeper/resource/default_voices"
}

logger_config = {
    "path": "",
    # "path": "/Users/liuzhanpeng/working/Keeper/logs/Childe/log.txt",
    "level": "DEBUG",
    "style": "",
}



salt = envs.get("SALT", "")
log_path = envs.get("LOG_PATH", "")
if salt:
    Config["salt"] = salt
if log_path:
    logger_config["path"] = log_path
