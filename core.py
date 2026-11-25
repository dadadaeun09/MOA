"""MOA 핵심 로직: 점수 계산, 정렬, 저장. (UI와 분리되어 있어 테스트하기 쉬움)"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

URGENT_DAYS = 3      # 남은 날짜가 이 값 이하이면 '임박'
URGENT_SCORE = 5     # 임박 점수
NORMAL_SCORE = 1     # 그 외 점수
DATA_FILE = Path.home() / ".moa" / "tasks.json"


@dataclass
class Task:
    title: str
    due: str            # "YYYY-MM-DD"
    importance: int     # 1 ~ 5
    done: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def days_left(self, today: date | None = None) -> int:
        """마감일 - 현재 날짜 (지난 일정은 음수)"""
        today = today or date.today()
        return (date.fromisoformat(self.due) - today).days

    def urgency_score(self, today: date | None = None) -> int:
        return URGENT_SCORE if self.days_left(today) <= URGENT_DAYS else NORMAL_SCORE

    def priority(self, today: date | None = None) -> int:
        """우선순위 점수 = 남은 날짜 점수 + 중요도"""
        return self.urgency_score(today) + self.importance


def sort_tasks(tasks: list[Task], today: date | None = None) -> list[Task]:
    """완료되지 않은 일정을 점수 내림차순으로 정렬 (동점이면 마감일이 빠른 순).
    완료된 일정은 맨 아래로 보낸다."""
    return sorted(
        tasks,
        key=lambda t: (t.done, -t.priority(today), t.due),
    )


def load_tasks(path: Path = DATA_FILE) -> list[Task]:
    if not path.exists():
        return []
    try:
        return [Task(**item) for item in json.loads(path.read_text(encoding="utf-8"))]
    except (json.JSONDecodeError, TypeError):
        return []


def save_tasks(tasks: list[Task], path: Path = DATA_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([asdict(t) for t in tasks], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
