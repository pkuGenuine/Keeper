from datetime import datetime, timedelta
from functools import wraps
# from hashlib import sha1
from Rex_Lapis.config import validation_config as config
from flask import jsonify, request
import json


# The auth scheme is not that secure but I want to make the system fast at first.

# Use the Authorization header so that the client can send the raw wave data without b64 encoding. 
# The usage of Authorization header is not standard.

# Because the communication is under https, I finally decided to use the dummy username:password auth method.
# Thus, device_name becomes the username and the salt becomes password.

salts = config["salts"]

def device_validate(fn):
    @wraps(fn)
    def wrapper(**kwargs):
        try:
            auth = request.headers["Authorization"]
            # Not standard Authorization header used!
            auth_scheme, content = tuple(auth.split())
            assert auth_scheme == "X-KeeperAuth"
            device_name, salt = tuple(content.split(";"))
            assert salts[device_name] == salt
        except:
            return jsonify(message=f"Unauthorized."), 401, {"Content-Type": "application/json"}
        return fn( **kwargs)
    return wrapper