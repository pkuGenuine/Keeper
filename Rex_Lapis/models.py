from Rex_Lapis import Morax
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy(Morax)
db.init_app(Morax)