from flask import Blueprint
from .auth import auth_blueprint
from .event import event_blueprint
from .user import user_blueprint

main_blueprint = Blueprint("my_calender", __name__)

main_blueprint.register_blueprint(auth_blueprint)
main_blueprint.register_blueprint(event_blueprint)
main_blueprint.register_blueprint(user_blueprint)
