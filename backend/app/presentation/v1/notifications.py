from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member
from app.infrastructure.repositories.notification_repository import SQLAlchemyNotificationRepository
from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository
from app.application.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/upcoming", summary="Upcoming notifications", description="Get actionable upcoming notifications grouped by today/this week")
async def upcoming_notifications(
    days: int = 7,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    event_repo = SQLAlchemyFinancialEventRepository(db)
    service = NotificationService(event_repo)
    return await service.get_upcoming(
        household_id=current_user["household_id"],
        days=days,
    )


@router.get("", summary="List notifications", description="Get all notifications for the current user")
async def list_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyNotificationRepository(db)
    return await repo.get_all(
        household_id=current_user["household_id"],
        user_id=current_user["id"],
        skip=skip,
        limit=limit,
    )


@router.get("/unread-count", summary="Unread count", description="Get count of unread notifications")
async def get_unread_count(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyNotificationRepository(db)
    count = await repo.get_unread_count(
        household_id=current_user["household_id"],
        user_id=current_user["id"],
    )
    return {"count": count}


@router.post("/{notification_id}/read", summary="Mark as read", description="Mark a notification as read")
async def mark_as_read(
    notification_id: str,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyNotificationRepository(db)
    result = await repo.mark_as_read(notification_id, current_user["household_id"])
    if not result:
        return {"status": "not_found"}
    await db.commit()
    return {"status": "ok"}


@router.post("/read-all", summary="Mark all as read", description="Mark all notifications as read")
async def mark_all_as_read(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyNotificationRepository(db)
    count = await repo.mark_all_as_read(
        household_id=current_user["household_id"],
        user_id=current_user["id"],
    )
    await db.commit()
    return {"marked": count}
