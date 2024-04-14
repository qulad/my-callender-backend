from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

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
