import json
import datetime
import os

# Under development
# Such a mess by now......

envs = os.environ

class FlaskConfig(object):
    """docstring for Config"""
    HOSTNAME='127.0.0.1'
    PORT='3306'
    DATABASE='Hermite'
    USERNAME='liuzhanpeng'
    PASSWORD=''
    DB_URI='mysql+pymysql://{username}:{password}@{host}:{port}/{db}'.format(
        username=USERNAME,
        password=PASSWORD,
        host=HOSTNAME,
        port=PORT,
        db=DATABASE,
    )
    SQLALCHEMY_DATABASE_URI=DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SECRET_KEY="SESSION_KEY_CHANGE_ME"


validation_config = {
    # No space is allowed in device name
    "salts": {
        "Registration": "Registration_Password_ChangeMe",
        "Raspberry_pi": "pi_salt_changeme",
    },
}


logger_config = {
    "path": "/Users/liuzhanpeng/working/Keeper/logs/Rex_Lapis/log.txt",
    "level": "DEBUG",
    "style": "",
}


voice2txt_config = {
    "api": "BaiduVoiceAPI",
    "token_url": "https://aip.baidubce.com/oauth/2.0/token",
    "api_key": {
        "grant_type":"client_credentials", 
        "client_id":"SaubuKzLp0ZHHdoa1YDjyxBn", 
        "client_secret": "2kUpGoDWd5LHbZ79VFf4Ylpq7GveFNrh"
    },
    "token_key": "refresh_token",
    "token_duration": {
        "days": 30,
    },
    "v2t_api_url": "http://vop.baidu.com/server_api",
    "t2v_api_url": "http://tsn.baidu.com/text2audio",
}

commands_config = {
    "expected_wakeup_word": "hey child",
}


if envs.get("FLASK_ENV", "") == "Product":
    port_number = envs.get("FLASK_PORT", "")
    db_uri      = envs.get("FLASK_DB_URI", "")
    if port_number:
        FlaskConfig.PORT = port_number
    if db_uri:
        FlaskConfig.SQLALCHEMY_DATABASE_URI = db_uri

log_level = envs.get("LOG_LEVEL", "")
log_path  = envs.get("LOG_PATH", "")
if log_level:
    logger_config["level"] = log_level
if log_path:
    logger_config["path"] = log_path