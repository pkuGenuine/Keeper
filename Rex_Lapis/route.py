from Rex_Lapis import Morax
from Rex_Lapis.auth import device_validate
from Rex_Lapis.models import db
from Rex_Lapis.logger import logger
from Rex_Lapis.utils import voice_api
from Rex_Lapis.commands import commands_handler
from flask import jsonify, request, send_file, session


@Morax.route("/wakeup", methods=["Post"])
@device_validate
def wakeup():

    # Used by "Childe" to double check the wakeup word.
    # As the local DNN model is not satisfying, forward the raw pcm data to 
    #   remote server, like baidu's API and convert it to text.
    # Then check the text (with commands module ) and return whether it is indeed a wakeup.
    # Also, based on some information, generate different voice_labels ( 
    #   like Good Morning ) for "Childe" to play.
    # It also sets up a session so later request, like the ones accessing "/commands"
    #   do not need to be authentication again.

    # In the future, the model in "Childe" ( light node ) will be moved to
    #   the device running this server.

    # require auth: True
    # input:        raw bytes
    # output:       json
    #     message:       Error msg ( On Failure )
    #     voice_labels:  list of voice labels for "Childe" to play, like ["Greeting"] ( On Success )

    response = voice_api.voice2txt(raw_data=request.data)
    message = "\n".join(response)
    if commands_handler.is_wakeup(message):
        session["wakeup"] = True
        message = "Wakeup Words detect: " + message
        logger.log(level="DEBUG", message=message)
        return commands_handler.make_wakeup_response()
    message = "Not a wakeup word: " + message
    logger.log(level="DEBUG", message=message)
    return jsonify(message=message), 200, {"Content-Type": "application/json"}


@Morax.route('/commands', methods=["Post"])
def commands():

    # After been awaken, "Childe" will send audios ( commands ) to with this API.
    # Should return quickly. If the commands can not be done in a jiffy, do it in an async manner.
    # It simply returns raw_voice or voice_labels for "Childe" to response.

    # Use remote API to convert the audio into text, and use the commands module to handle texts.
    # Basically it will return raw pcm voice ( 
    #   synthesized with baidu'api ) for "Childe" to play.
    # But also possible to return voice labels and other message in json format.
    # Use "Content-Type" response header to distinguish these two types.

    # require auth: False  ( Used in an authorized session. )
    # input:        raw bytes
    # output:       json/raw_bytes ( depends on "Content-Type" response header )
    #   ( If Content-Type is json )
    #     voice_labels   ( On Success )
    #     message        ( On Failure )

    if not session.get("wakeup", False):
        return jsonify(message=f"Unauthorized."), 401, {"Content-Type": "application/json"}

    response = voice_api.voice2txt(raw_data=request.data)
    command = "\n".join(response)
    logger.log(level="DEBUG", message="Analyzing:" + command)
    return commands_handler.execute_commands(command)


@Morax.route("/device_register", methods=["Post"])
@device_validate
def device_register():

    # Under development.

    raw_data=request.data
    raise NotImplementedError

