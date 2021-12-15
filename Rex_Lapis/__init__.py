"""
Internal Dependency:
    __init__.py
    -> route.py
    -> commands.py
    -> skills.py
    -> model.py
    -> auth.py
    -> utils.py
    -> logger.py
    -> config.py
"""

from flask import Flask
from Rex_Lapis.config import FlaskConfig

Morax = Flask(__name__)
Morax.config.from_object(FlaskConfig)

from Rex_Lapis.models import db
from Rex_Lapis.route import *