from .. import db

class EventEntity(db.model):
    id = db.Column(db.Text, primary_key=True) # uuid v4
    location = db.Column(db.Text)
    creator_user_name = db.Column(db.Text)
    date_time = db.Column(db.DateTime)
    description = db.Column(db.Text)
