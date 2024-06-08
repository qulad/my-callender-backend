from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import re

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "my_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

jwt = JWTManager(app)

db = SQLAlchemy()
db.init_app(app)

def create_db():
    with app.app_context():
        db.create_all()

#region dtos
@dataclass
class EventDto:
    id: UUID
    created_by: str
    location: str
    date_time: datetime
    description: str
    invited_user_names: list
    accepted_user_names: list
    rejected_user_names: list
@dataclass
class UserDto:
    id: int
    profile_photo: str
    user_name: str
    full_name: str
    biography: str
    friends: list
    received_friend_requests: list
    sent_friend_requests: list
    blocked: list
    password: str
    email: str
#endregion

#region entities
class BlockedEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blocker_user_name = db.Column(db.Text)
    blocked_user_name = db.Column(db.Text)

class EventEntity(db.Model):
    id = db.Column(db.Text, primary_key=True) # uuid v4
    location = db.Column(db.Text)
    creator_user_name = db.Column(db.Text)
    date_time = db.Column(db.DateTime)
    description = db.Column(db.Text)
    
class FriendsEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accepted = db.Column(db.Boolean)
    requester_user_name = db.Column(db.Text)
    responder_user_name = db.Column(db.Text)
    
class InvitesEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Text)
    status = db.Column(db.Integer) # enum
    requester_user_name = db.Column(db.Text)
    responder_user_name = db.Column(db.Text)
    
class UserEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_photo = db.Column(db.Text)
    user_name = db.Column(db.Text)
    email = db.Column(db.Text)
    full_name = db.Column(db.Text)
    biography = db.Column(db.Text)
    password = db.Column(db.Text)
#endregion

#region repositories
class BlockedRepository:
    def get_blocked_list_by_blocker_user_name(self, blocker_user_name : str) -> list:
        blocks : list = BlockedEntity.query.filter_by(blocker_user_name=blocker_user_name).all()

        if blocks is None:
            return []

        blocked = []

        block : BlockedEntity
        for block in blocks:
            blocked.append(block.blocked_user_name)

        return blocked
    
class EventRepository:
    def get_events_with_limit(self, limit : int) -> List[EventDto]:
        event_entities = EventEntity.query.limit(limit).all()
        
        if event_entities is None:
            return []
        
        events = []
        
        event_entity : EventEntity
        for event_entity in event_entities:
            event = EventDto(
                id=event_entity.id,
                created_by=event_entity.creator_user_name,
                location=event_entity.location,
                date_time=event_entity.date_time,
                description=event_entity.description,
                invited_user_names=[],
                accepted_user_names=[],
                rejected_user_names=[]
            )
            
            invites_entities = InvitesEntity.query.filter_by(event_id=event_entity.id).all()
            
            if invites_entities is None:
                events.append(event)
                continue
            
            invite : InvitesEntity
            for invite in invites_entities:
                if invite.status == 0:
                    event.invited_user_names.append(invite.responder_user_name)
                elif invite.status == 1:
                    event.accepted_user_names.append(invite.responder_user_name)
                elif invite.status == 2:
                    event.rejected_user_names.append(invite.responder_user_name)
            
            events.append(event)
        
        return events

    def reject_event_invite(self, event_id : uuid, user_name : str):
        invite_entity = InvitesEntity.query.filter_by(
            event_id=event_id,
            responder_user_name=user_name
        ).first()
        
        if invite_entity is None:
            return False
        
        invite_entity.status = 2
        db.session.commit()
        return True

    def accept_event_invite(self, event_id : uuid, user_name : str):
        invite_entity = InvitesEntity.query.filter_by(
            event_id=event_id,
            responder_user_name=user_name
        ).first()
        
        if invite_entity is None:
            return False
        
        invite_entity.status = 1
        db.session.commit()
        return True

    def add_event(self, created_by: str, invites : List[str], location : str, date : datetime, description : str) -> uuid:
        event_entity = EventEntity(
            id=str(uuid.uuid4()),
            location=location,
            creator_user_name=created_by,
            date_time=datetime.strptime(date, '%Y-%m-%dT%H:%M'),
            description=description)
        
        db.session.add(event_entity)
        
        if len(invites) > 0:
            for invite in invites:
                invites_entity = InvitesEntity(
                    event_id=event_entity.id,
                    status=0,
                    requester_user_name=created_by,
                    responder_user_name=invite)
        
                db.session.add(invites_entity)
        db.session.commit()
        
        return event_entity.id
        
    def check_if_event_id_valid(self, event_id : uuid) -> bool:
        event_entity = EventEntity.query.filter_by(id=event_id).first()
        return event_entity is not None

    def get_event_from_event_id(self, event_id : uuid) -> EventDto:
        event_entity = EventEntity.query.filter_by(id=event_id).first()
        
        if event_entity is None:
            return None
        
        event = EventDto(
            id=event_entity.id,
            created_by=event_entity.creator_user_name,
            location=event_entity.location,
            date_time=event_entity.date_time,
            description=event_entity.description,
            invited_user_names=[],
            accepted_user_names=[],
            rejected_user_names=[]
        )
        
        invites_entities = InvitesEntity.query.filter_by(event_id=event_id).all()
        
        if invites_entities is None:
            return event
        
        invite : InvitesEntity
        for invite in invites_entities:
            if invite.status == 0:
                event.invited_user_names.append(invite.responder_user_name)
            elif invite.status == 1:
                event.accepted_user_names.append(invite.responder_user_name)
            elif invite.status == 2:
                event.rejected_user_names.append(invite.responder_user_name)
        
        return event

class FriendsRepository:
    def get_received_friend_requests_list_by_user_name(self, user_name : str) -> list:
        friends_entities = FriendsEntity.query.filter_by(accepted=False, responder_user_name=user_name).all()

        if friends_entities is None:
            return []

        received_from = []

        friends_entity : FriendsEntity
        for friends_entity in friends_entities:
            received_from.append(friends_entity.requester_user_name)

        return received_from

    def get_sent_friend_requests_list_by_user_name(self, user_name : str) -> list:
        friends_entities = FriendsEntity.query.filter_by(accepted=False, requester_user_name=user_name).all()

        if friends_entities is None:
            return []

        sent_to = []

        friends_entity : FriendsEntity
        for friends_entity in friends_entities:
            sent_to.append(friends_entity.responder_user_name)

        return sent_to

    def get_friends_list_by_user_name(self, user_name : str) -> list:
        friends_entities = FriendsEntity.query.filter(
            db.and_(
                FriendsEntity.accepted == True,
                db.or_(
                    FriendsEntity.requester_user_name == user_name,
                    FriendsEntity.responder_user_name == user_name
                )
            )
        ).all()

        if friends_entities is None:
            return []

        friends = []

        friends_entity : FriendsEntity
        for friends_entity in friends_entities:
            if friends_entity.requester_user_name == user_name:
                friends.append(friends_entity.requester_user_name)
            else:
                friends.append(friends_entity.responder_user_name)

        return friends
    
class UserRepository:
    def get_user_by_user_entity(self, user_entity : UserEntity) -> UserDto:
        if user_entity is None:
            return None
        
        user_name = user_entity.user_name

        blocked_list = BlockedRepository().get_blocked_list_by_blocker_user_name(user_name)
        sent_friend_requests = FriendsRepository().get_sent_friend_requests_list_by_user_name(user_name)
        received_friend_requests = FriendsRepository().get_received_friend_requests_list_by_user_name(user_name)
        friend_list = FriendsRepository().get_friends_list_by_user_name(user_name)
        
        user = UserDto(
            id=user_entity.id,
            profile_photo=user_entity.profile_photo,
            user_name=user_entity.user_name,
            full_name=user_entity.full_name,
            biography=user_entity.biography,
            friends=friend_list,
            received_friend_requests=received_friend_requests,
            sent_friend_requests=sent_friend_requests,
            blocked=blocked_list,
            password=user_entity.password,
            email=user_entity.email
        )
        
        return user

    def get_user_by_email(self, email : str) -> UserDto:
        user_entity = UserEntity.query.filter_by(email=email).first()
        return self.get_user_by_user_entity(user_entity)

    def get_user_by_user_name(self, user_name : str) -> UserDto:
        user_entity = UserEntity.query.filter_by(user_name=user_name).first()
        return self.get_user_by_user_entity(user_entity)
    
    def add_user(self, user : UserDto):
        user_entity = UserEntity(
            profile_photo=user.profile_photo,
            user_name=user.user_name,
            email=user.email,
            full_name=user.full_name,
            biography=user.biography,
            password=user.password
        )
        
        db.session.add(user_entity)
        db.session.commit()
        
    def handle_block_request(self, blocker_user_name : str, blocked_user_name : str):
        blocked_entity = BlockedEntity.query.filter_by(
            blocker_user_name=blocker_user_name,
            blocked_user_name=blocked_user_name
        ).first()
        
        if blocked_entity is None:
            blocked_entity = BlockedEntity(
                blocker_user_name=blocker_user_name,
                blocked_user_name=blocked_user_name
            )
            
            db.session.add(blocked_entity)
            db.session.commit()
        else:
            db.session.delete(blocked_entity)
            db.session.commit()
        
    def handle_friend_request(self, requester_user_name : str, responder_user_name : str):
        friends_entity = FriendsEntity.query.filter_by(
            requester_user_name=requester_user_name,
            responder_user_name=responder_user_name
        ).first()
        
        if friends_entity is None:
            friends_entity = FriendsEntity(
                accepted=False,
                requester_user_name=requester_user_name,
                responder_user_name=responder_user_name
            )
            
            db.session.add(friends_entity)
            db.session.commit()
        else:
            if friends_entity.accepted:
                db.session.delete(friends_entity)
                db.session.commit()
            else:
                friends_entity.accepted = True
                db.session.commit()
#endregion

#region endpoints

#region auth
@app.post("/auth/login")
def login():
    username = request.json.get("userName", None)
    password = request.json.get("password", None)
    
    if not username or not password:
        return jsonify({}), 400
    
    user_repository = UserRepository()
    
    user = user_repository.get_user_by_user_name(username)
    if user is None:
        return jsonify({}), 404
    
    if user.password != password:
        return jsonify({}), 401

    token = create_access_token(identity=username)
    return jsonify(access_token=token), 200

@app.post("/auth/register")
def register():
    user_repository = UserRepository()
    email = request.json.get("email", None)
    username = request.json.get("userName", None)
    full_name = request.json.get("fullName", None)
    password = request.json.get("password", None)
    password2 = request.json.get("password2", None)
    
    if not email or not username or not full_name or not password or not password2:
        return jsonify({}), 400
    
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.match(regex, email) is None:
        return jsonify({}), 422

    if password != password2:
        return jsonify({}), 417
    
    user = user_repository.get_user_by_email(email)
    if user is not None:
        return jsonify({}), 409
    
    user = user_repository.get_user_by_user_name(username)    
    if user is not None:
        return jsonify({}), 412
    
    user = UserDto(
        id=0,
        profile_photo="",
        user_name=username,
        full_name=full_name,
        biography="",
        friends=[],
        received_friend_requests=[],
        sent_friend_requests=[],
        blocked=[],
        password=password,
        email=email)
    user_repository.add_user(user)
    
    token = create_access_token(identity=username)
    return jsonify(access_token=token), 201

@app.post("/auth/logout")
@jwt_required()
def logout():
    return jsonify({}), 200
#endregion

#region user
@app.get("/user/<string:username>")
def user_details(username):
    user_repository = UserRepository()
    user = user_repository.get_user_by_user_name(username)
    
    if user is None:
        return jsonify({}), 404
    
    return jsonify(user), 200

@app.get("/user/me", endpoint="user_details_me")
@jwt_required()
def user_details_me():
    username = get_jwt_identity()
    user_repository = UserRepository()
    user = user_repository.get_user_by_user_name(username)
    
    if user is None:
        return jsonify({}), 404
    
    return jsonify(user), 200

@app.delete("/user/friends", endpoint="user_friends")
@app.get("/user/friends", endpoint="user_friends")
@app.post("/user/friends", endpoint="user_friends")
@jwt_required()
def user_friends():
    username_to_add = request.json.get("userName", None)
    if username_to_add is None:
        return jsonify({}), 400
    
    user_repository = UserRepository()
    
    user_to_add = user_repository.get_user_by_user_name(username_to_add)
    if user_to_add is None:
        return jsonify({}), 404
    
    username = get_jwt_identity()
    user = user_repository.get_user_by_user_name(username)
    
    if user is None:
        return jsonify({}), 404
    
    user_repository.handle_friend_request(user.user_name, user_to_add.user_name)
    
    return jsonify(friends=user.friends), 200

@app.delete("/user/blocked", endpoint="user_blocked")
@app.get("/user/blocked", endpoint="user_blocked")
@app.post("/user/blocked", endpoint="user_blocked")
@jwt_required()
def user_blocked():
    username_to_add = request.json.get("userName", None)
    if username_to_add is None:
        return jsonify({}), 400
    
    user_repository = UserRepository()
    
    user_to_add = user_repository.get_user_by_user_name(username_to_add)
    if user_to_add is None:
        return jsonify({}), 404
    
    username = get_jwt_identity()
    user = user_repository.get_user_by_user_name(username)
    
    if user is None:
        return jsonify({}), 404
    
    user_repository.handle_block_request(user.user_name, user_to_add.user_name)
    
    return jsonify(friends=user.friends), 200
#endregion

#region event
@app.get("/event/<uuid:event_id>")
@jwt_required()
def get_event_details(event_id):
    event_repository = EventRepository()
    
    if not event_repository.check_if_event_id_valid(event_id):
        return jsonify({}), 404
    
    event = event_repository.get_event_from_event_id(event_id)
    
    return jsonify(event), 200

@app.get("/event")
@jwt_required()
def get_events_with_limit():
    limit = 20
    event_repository = EventRepository()
    
    events = event_repository.get_events_with_limit(limit)
    
    return jsonify(events), 200

@app.post("/event")
@jwt_required()
def add_event():
    location = request.json.get("location", None)
    date = request.json.get("date", None)
    description = request.json.get("description", None)
    invites = request.json.get("invites", [])
    
    if not location and not date and not description:
        return jsonify({}), 400
    
    event_repository = EventRepository()
    
    event_id = event_repository.add_event(get_jwt_identity(), invites, location, date, description)
    
    return jsonify(event_id=event_id), 200

@app.put("/event/<uuid:event_id>")
@jwt_required()
def accept_event_invite(event_id):
    event_repository = EventRepository()
    
    if not event_repository.check_if_event_id_valid(event_id):
        return jsonify({}), 404
    
    accepted = event_repository.accept_event_invite(event_id, get_jwt_identity())
    
    if accepted:
        return jsonify({}), 200
    return jsonify({}), 409

@app.delete("/event/<uuid:event_id>")
@jwt_required()
def reject_event_invite(event_id):
    event_repository = EventRepository()
    
    if not event_repository.check_if_event_id_valid(event_id):
        return jsonify({}), 404
    
    rejected = event_repository.reject_event_invite(event_id, get_jwt_identity())
    
    if rejected:
        return jsonify({}), 200
    return jsonify({}), 409
#endregion

#endregion

if __name__ == "__main__":
    print(app.url_map)
    # create_db()
    app.run(port=5000, debug=True)