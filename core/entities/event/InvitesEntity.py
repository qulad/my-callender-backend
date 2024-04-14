from .. import db

class InvitesEntity(db.model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Text)
    status = db.Column(db.Integer) # enum
    requester_user_name = db.Column(db.Text)
    responder_user_name = db.Column(db.Text)
