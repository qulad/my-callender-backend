from .. import db

class UserEntity(db.model):
    id = db.Column(db.Integer, primary_key=True)
    profile_photo = db.Column(db.Text)
    user_name = db.Column(db.Text)
    email = db.Column(db.Text)
    full_name = db.Column(db.Text)
    biography = db.Column(db.Text)
    password = db.Column(db.Text)
