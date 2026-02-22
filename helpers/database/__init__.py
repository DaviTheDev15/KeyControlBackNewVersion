from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from helpers.application import app
from flask_migrate import Migrate


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)