from Rex_Lapis.config import commands_config
from Rex_Lapis.skills import skill_map
from Rex_Lapis.logger import logger
from Rex_Lapis.utils import voice_api
from flask import jsonify

class CommandsHandler(object):
    """docstring for CommandHandler"""

    # CommandHandler
    # Handle wakeup and commands based on text and background information.

    # For text commands, the commands module parse the command and dispatch
    #   the task to "skills". It works as follow:
    #   1. Based on text, map it to a "skill" and extract the arguments.
    #   2. Invocate appropriate function in skills module with the extracted arguments.
    #       ( It is also possible to pass the whole text to handling function. )
    #   3. Make http response based on handling function's return value.

    # The command module also does wakeup handling.
    # It checks the key word. If match, call the "wakeup_response" skill to
    #   generate voice labels.

    # Handler functions should return a tuple:
    #     status:        "OK"/"Pending"/"Error"
    #     content_type:  "text"/"labels"
    #     data           


    def __init__(self):
        super(CommandsHandler, self).__init__()
        self.expected_wakeup_word = commands_config["expected_wakeup_word"]

    def is_wakeup(self, text):

        # Not a good implementation
        if self.expected_wakeup_word.lower() in text.lower() or text.lower() == "Child".lower():
            return True
        return False

        return self.expected_wakeup_word.lower() in text.lower()

    def make_wakeup_response(self):

        try:
            _, _, voice_labels = skill_map["wakeup_response"]()
            return jsonify(voice_labels=voice_labels), 200, {"Content-Type": "application/json"}

        except:
            logger.log(level="CRITICAL", message="Failed to make response.")
            return jsonify(message="Unexpected Error."), 200, {"Content-Type": "application/json"}


    def map2skill(self, text):

        # Parsing the text

        # Under development, just a demo here
        text = text.lower()
        if "how" in text or "what" in text:
            return "query", {"about": "", "constraints": ""}

        if "which" in text or "choose" in text or "pick up" in text:
            return "choice", {"about": "", "constraints": ""}

        # if "music" in text or "song" in text:
        #     return "Music", {}

        if "good night" in text:
            return "chit_chat", {"labels": ["Night"]}

        return "fallback", {}


    def execute_commands(self, text):
        skill, kwargs = self.map2skill(text)

        # Dispatch the task

        if not skill in skill_map:
            logger.log(level="CRITICAL", message=f"Unsupported skill {skill}. ( Unexpected )")
            skill = "error_report"
            kwargs = {}

        status, content_type, content = skill_map[skill](**kwargs)

        if not content:
            content_type = "labels"
            # Use default actions based on status
            content = ["Diluc_OK"] if status == "OK" else (["Albedo_Understood"] if status == "Pending" else ["Error"])

        response = voice_api.txt2voice(content) if content_type == "text" else jsonify(voice_labels=content)
        headers = {"Content-Type": voice_api.response_audio_type if content_type == "text" else "application/json"}

        return response, 200, headers


commands_handler = CommandsHandler()
        