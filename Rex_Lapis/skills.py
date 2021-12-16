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
def wakeup_response(skill, *args, **kwargs):
    
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
        voice_labels.append("AfterDinner")
    else:
        voice_labels.append("Comrade")
        voice_labels.append("Urge")
        # voice_labels.append("Diluc_Needs")
    return "OK", "labels", voice_labels


# Under development, just a demo here
@Skill("entrace_record")
def entrace_record(skill):
    return "OK", "labels", ["Albedo_Understood"]



from multiprocessing import Process
def f():
    import time, os
    import playsound
    time.sleep(1)
    dir_path = "/Users/liuzhanpeng/working/Keeper/resource/music"
    file_name = "test.mp3"
    playsound(os.path.join(dir_path, file_name))
    # os.system(f"open {os.path.join(dir_path, file_name)}")

@Skill("Music")
def music(skill):

    p = Process(target=f)
    p.start()

    # zombie, no reap here
    return "OK", "labels", ["Albedo_Understood"]

@Skill("chit_chat")
def chit_chat(skill, labels):
    return "OK", "labels", labels

@Skill("query")
def query(skill, about, constraints):
    return "OK", "labels", ["Windy"]

@Skill("choice", attr_dict={})
def choice(skill, about, constraints):
    return "OK", "text", "I recommand 学一" 

@Skill("fallback")
def fallback(skill):
    return "OK", "labels", ["Not_Understand"]

@Skill("error_report")
def error_report(skill):
    return "Error", None, None
        
skill_map = {
    wakeup_response.skill_name: wakeup_response,  
    chit_chat.skill_name:       chit_chat,
    query.skill_name:           query,
    fallback.skill_name:        fallback,
    error_report.skill_name:    error_report,
    music.skill_name:           music,
    entrace_record.skill_name:  entrace_record,
    choice.skill_name:          choice,
}