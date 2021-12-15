from Rex_Lapis.config import commands_config
from Rex_Lapis.skills import skill_map
from Rex_Lapis.logger import logger
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
    #     status:        "Finishing"/"Pending"/"Error"
    #     content_type:  "raw"/"text"/"json_string"/"string_list"
    #     data

    def __init__(self):
        super(CommandsHandler, self).__init__()
        self.expected_wakeup_word = commands_config["expected_wakeup_word"]

    def is_wakeup(self, text):

        # Should not be commited codes:
        if self.expected_wakeup_word.lower() in text.lower() or text.lower() == "Child".lower():
            return True
        return False

        return self.expected_wakeup_word.lower() in text.lower()

    def make_wakeup_response(self):

        try:
            _, _, voice_labels = skill_map["wakeup_response"]()
            return jsonify(wakeup=True, voice_labels=voice_labels), 200, {"Content-Type": "application/json"}

        except:
            logger.log(level="CRITICAL", message="Failed to make response.")
            return jsonify(wakeup=False, message="Expected Error."), 200, {"Content-Type": "application/json"}


        return jsonify(wakeup=True)

    def map2skill(self, text):

        # Parsing the text

        skill = ""
        args = ""
        return skill, args


    def execute_commands(self, text):
        skill, args = map2skill(text)

        # Dispatch the task

        if not skill in skill_map:
            d = {
                "status_code": 405,
                "message"    : "Unsupported skill."
            }
            return jsonify(**d), 200, {"Content-Type": "application/json"}
        if skill_map[skill] is not None:
            status, content_type, content = skill_map[skill](args)
        else:
            logger.log(level="INFO", message=f"Unsupported skill")
            return jsonify()

        if status == "Finished":
            status_code = 200
        elif status == "Pending":
            status_code = 200
        elif status == "Error":
            status_code = 200
        else:
            raise NotImplementedError

        return {"status": "Finished", "message": text}


commands_handler = CommandsHandler()
        