import json
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import NotificationModel, UserModel


class SQLAlchemyNotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, household_id: str, user_id: Optional[str] = None, skip: int = 0, limit: int = 50):
        query = select(NotificationModel).where(NotificationModel.household_id == household_id)
        if user_id:
            query = query.where(NotificationModel.user_id == user_id)
        query = query.order_by(NotificationModel.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        notifications = result.scalars().all()
        return [self._to_dict(n) for n in notifications]

    @staticmethod
    def _to_dict(notification: NotificationModel) -> dict:
        return {
            "id": notification.id,
            "household_id": notification.household_id,
            "user_id": notification.user_id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "data": notification.data,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
        }

    async def get_unread_count(self, household_id: str, user_id: str) -> int:
        query = select(func.count(NotificationModel.id)).where(
            NotificationModel.household_id == household_id,
            NotificationModel.user_id == user_id,
            NotificationModel.is_read == False,
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def create(self, data: dict):
        notification = NotificationModel(**data)
        self.session.add(notification)
        await self.session.flush()
        await self.session.refresh(notification)
        return dict(notification)

    async def mark_as_read(self, notification_id: str, household_id: str):
        query = select(NotificationModel).where(
            NotificationModel.id == notification_id,
            NotificationModel.household_id == household_id,
        )
        result = await self.session.execute(query)
        notification = result.scalar_one_or_none()
        if notification:
            notification.is_read = True
            await self.session.flush()
            return dict(notification)
        return None

    async def mark_all_as_read(self, household_id: str, user_id: str):
        query = select(NotificationModel).where(
            NotificationModel.household_id == household_id,
            NotificationModel.user_id == user_id,
            NotificationModel.is_read == False,
        )
        result = await self.session.execute(query)
        notifications = result.scalars().all()
        for n in notifications:
            n.is_read = True
        await self.session.flush()
        return len(notifications)

    async def notify_household_members(
        self,
        household_id: str,
        exclude_user_id: str,
        title: str,
        message: str,
        data: Optional[dict] = None,
    ) -> int:
        """Create a notification for every household member except the excluded one."""
        result = await self.session.execute(
            select(UserModel).where(
                UserModel.household_id == household_id,
                UserModel.id != exclude_user_id,
            )
        )
        members = result.scalars().all()
        count = 0
        for member in members:
            notification = NotificationModel(
                household_id=household_id,
                user_id=member.id,
                type="family_event",
                title=title,
                message=message,
                data=json.dumps(data) if data else None,
            )
            self.session.add(notification)
            count += 1
        await self.session.flush()
        return count
