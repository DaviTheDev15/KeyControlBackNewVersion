from flask_cors import CORS
from helpers.application import app

cors = CORS(app, 
            supports_credentials=True, 
            origins=["http://localhost:5173"],
            allow_headers=["Content-Type", "Authorization"],
            methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])