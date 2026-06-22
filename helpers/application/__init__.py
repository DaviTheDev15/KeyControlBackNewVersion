from datetime import timedelta
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Souza30072005@localhost:5432/keycontrol"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False  # dev
app.config["JWT_COOKIE_SAMESITE"]     = "Lax" 
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
# app.config['SQLALCHEMY_ECHO'] = True

api = Api(app)

jwt = JWTManager(app)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {"message": "Token expirado"}, 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return {"message": error}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {"message": error}, 401