from main import app
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)

def create_all():
    from .entities.event import EventEntity, InvitesEntity
    from .entities.user import BlockedEntity, FriendsEntity, UserEntity
    with app.app_context():
        db.create_all()
