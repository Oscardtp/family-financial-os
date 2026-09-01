from datetime import date, timedelta


class NotificationService:
    def __init__(self, event_repo):
        self.event_repo = event_repo

    async def get_upcoming(self, household_id: str, as_of: date | None = None, days: int = 7) -> dict:
        as_of = as_of or date.today()
        events = await self.event_repo.get_upcoming(household_id, as_of, days, include_overdue=True)
        today_items: list[dict] = []
        week_items: list[dict] = []
        for event in events:
            due = event.get("due_date")
            if not due:
                continue
            if isinstance(due, str):
                due = date.fromisoformat(due)
            item = {
                "event_id": event["id"],
                "title": event.get("title", ""),
                "amount": event.get("amount"),
                "due_date": due.isoformat(),
                "type": event.get("type"),
                "obligation_id": event.get("obligation_id"),
            }
            if due < as_of:
                item["level"] = "Pendiente"
                today_items.append(item)
            elif due == as_of:
                item["level"] = "Hoy"
                today_items.append(item)
            elif due == as_of + timedelta(days=1):
                item["level"] = "Mañana"
                week_items.append(item)
            elif due <= as_of + timedelta(days=3):
                item["level"] = "Se acerca"
                week_items.append(item)
            elif due <= as_of + timedelta(days=7):
                item["level"] = "Próximamente"
                week_items.append(item)
        return {
            "today": today_items,
            "this_week": week_items,
        }
