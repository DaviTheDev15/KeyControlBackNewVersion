from flask import Flask
from flask_restful import Api

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Souza30072005@keycontrol-db:5432/keycontrol"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config['SQLALCHEMY_ECHO'] = True

api = Api(app)