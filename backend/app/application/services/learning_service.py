from collections import defaultdict
from datetime import timedelta
from decimal import Decimal


class LearningService:
    def __init__(self, session):
        self.session = session

    async def detect_patterns(self, household_id: str) -> list[dict]:
        from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
        from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository
        tx_repo = SQLAlchemyTransactionRepository(self.session)
        event_repo = SQLAlchemyFinancialEventRepository(self.session)
        txs = await tx_repo.get_all(household_id, limit=500)
        events = await event_repo.get_all(household_id, limit=500)

        groups = defaultdict(list)
        for tx in txs:
            desc = (tx.get("description") or "").strip()
            if not desc:
                continue
            groups[("tx", desc.lower())].append(tx)

        for ev in events:
            if ev.get("status") != "paid":
                continue
            title = (ev.get("title") or "").strip()
            if not title:
                continue
            groups[("event", title.lower())].append(ev)

        suggestions = []
        for (source, name), items in groups.items():
            if len(items) < 3:
                continue
            items.sort(key=lambda t: t.get("date") or t.get("due_date") or "")
            best = self._best_cluster(items)
            if best is None or len(best) < 3:
                continue
            amounts = [Decimal(str(t.get("amount") or 0)) for t in best]
            avg = sum(amounts) / len(amounts)
            variance = max(abs(a - avg) / avg for a in amounts) if avg else Decimal("0")
            confidence = 100 - int(variance * 100)
            confidence = max(confidence, 50)
            anchor = best[0].get("date") if source == "tx" else best[0].get("due_date")
            if hasattr(anchor, "day"):
                anchor = anchor.day
            elif isinstance(anchor, str):
                try:
                    anchor = __import__("datetime").date.fromisoformat(anchor).day
                except Exception:
                    anchor = None
            suggestions.append({
                "name": name.title(),
                "type": best[0].get("type", "expense"),
                "amount": avg,
                "confidence": confidence,
                "occurrences": len(best),
                "anchor_day": anchor,
                "source": "LEARNED",
                "visibility": "estimated",
            })

        suggestions.sort(key=lambda s: s["confidence"], reverse=True)
        return suggestions

    @staticmethod
    def _best_cluster(items: list[dict]) -> list[dict] | None:
        dates = []
        for t in items:
            d = t.get("date") or t.get("due_date")
            if hasattr(d, "strftime"):
                dates.append((d, t))
            elif isinstance(d, str):
                try:
                    dates.append((__import__("datetime").date.fromisoformat(d), t))
                except Exception:
                    continue
        dates.sort(key=lambda x: x[0])
        best = []
        for i in range(len(dates)):
            cluster = [dates[j][1] for j in range(len(dates)) if abs((dates[j][0] - dates[i][0]).days) <= 3]
            if len(cluster) > len(best):
                best = cluster
        return best or None
