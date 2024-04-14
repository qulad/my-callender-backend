from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

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
