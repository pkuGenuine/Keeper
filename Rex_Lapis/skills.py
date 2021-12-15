import requests
from functools import wraps
from datetime import datetime, timedelta
from flask import jsonify

class Skill(object):
    
    # Skill
    # A wrapper class to enclose skill functions.

    def __init__(self, name, map_device="local", attr_dict={}):
        super(Skill, self).__init__()

        # Probably add more features later.

        self.skill_name = name
        self.map_device = map_device
        self.attr_dict = attr_dict

    # Can not override __call__ as magic methods are all Class specific.
    # Add a "call_method" to be overrided
    def __call__(self, *args, **kwargs):
        return self.call_method(*args, **kwargs)

    def call_method(self, func):
        # Adding wraps results into a bug.
        # Dive into it later......
        # @wraps
        def wrapped_function(*args, **kwargs):

            # Default is http post request
            # Under development

            if func is None and self.map_device != "local":
                try:
                    r = requests.post(*args, **kwargs)

                    error_message = "NotImplementedError"
                    raise NotImplementedError
                except:
                    error_message = "Request failed."
                    pass
                return "Error", "application/json", jsonify(message=error_message)

            return func(self, *args, **kwargs)

        self.call_method = wrapped_function
        return self 

    def update_attr_dict(self, d):
        self.attr_dict.update(d)

@Skill("wakeup_response", attr_dict={"last_special_day": datetime.now() - timedelta(days=1)})
def wakeup_response(skill):
    
    def special_day_first_time(skill, month, day):
        cur_time = datetime.now()
        if cur_time.month != month or cur_time.day != day:
            return False
        last_special_day = skill.attr_dict["last_special_day"]
        if last_special_day.month == cur_time.month and last_special_day.day == cur_time.day:
            return False
        skill.attr_dict["last_special_day"] = cur_time
        return True

    now_hour = datetime.now().hour
    voice_labels = []

    if special_day_first_time(skill, 5, 8):
        # status, content_type, content
        voice_labels.append("Birthday")
    elif 6 <= now_hour < 11:
        voice_labels.append("Morning")
    elif 11 <= now_hour < 17:
        voice_labels.append("Comrade")
        voice_labels.append("Urge")
    elif 17 <= now_hour < 19:
        voice_labels.append("After_dinner")
    else:
        voice_labels.append("Diluc_Needs")

    return "Finished", "string_list", voice_labels
        
skill_map = {
    wakeup_response.skill_name: wakeup_response,  
}