from ... import db

class FriendsEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accepted = db.Column(db.Boolean)
    requester_user_name = db.Column(db.Text)
    responder_user_name = db.Column(db.Text)
