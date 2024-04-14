from ...entities.user.UserEntity import UserEntity
from ...dto.UserDto import UserDto
from .BlockedRepository import BlockedRepository
from .FriendsRepository import FriendsRepository

class UserRepository:
    def get_user_by_user_name(self, user_name : str) -> UserDto:
        user_entity = UserEntity.query.filter_by(user_name=user_name).first()
        if user_entity is None:
            return None

        blocked_list = BlockedRepository.get_blocked_list_by_blocker_user_name(user_name)
        sent_friend_requests = FriendsRepository.get_sent_friend_requests_list_by_user_name(user_name)
        received_friend_requests = FriendsRepository.get_received_friend_requests_list_by_user_name(user_name)
        friend_list = FriendsRepository.get_friends_list_by_user_name(user_name)
        
        user = UserDto(
            id=user_entity.id,
            profile_photo=user_entity.profile_photo,
            user_name=user_entity.user_name,
            full_name=user_entity.full_name,
            biography=user_entity.biography,
            friends=friend_list,
            received_friend_requests=received_friend_requests,
            sent_friend_requests=sent_friend_requests,
            blocked_list=blocked_list,
            password=user_entity.password,
            email=user_entity.email
        )
        
        return user