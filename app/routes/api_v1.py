from flask import Blueprint
from ..controllers.api.auth_controller import auth_bp

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v1.register_blueprint(auth_bp)


