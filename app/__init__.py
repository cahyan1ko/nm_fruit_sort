from flask import Flask
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret-key"
    
    swagger = Swagger(app)

    from .routes.web import main
    app.register_blueprint(main)

    from .routes.api_v1 import api_v1
    app.register_blueprint(api_v1)

    return app
