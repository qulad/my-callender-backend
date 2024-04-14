from ... import db

class BlockedEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blocker_user_name = db.Column(db.Text)
    blocked_user_name = db.Column(db.Text)
