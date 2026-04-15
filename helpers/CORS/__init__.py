from flask_cors import CORS
from helpers.application import app

cors = CORS(app, resources={r"/*": {"origins": "*"}})