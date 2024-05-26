from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from application import main_blueprint

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "my_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

jwt = JWTManager(app)

app.register_blueprint(main_blueprint, url_prefix="/")

db = SQLAlchemy()

def create_db():
    from core.entities.event import EventEntity, InvitesEntity
    from core.entities.user import BlockedEntity, FriendsEntity, UserEntity
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    
    print(app.url_map)
    db.init_app(app)
    create_db()
    app.run(port=5000, debug=True)