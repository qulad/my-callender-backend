from ...entities.user.FriendsEntity import FriendsEntity
from ... import db

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
    