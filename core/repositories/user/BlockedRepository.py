from ...entities.user.BlockedEntity import BlockedEntity

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
