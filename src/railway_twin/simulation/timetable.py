from typing import Dict, List, Optional

class TimetableEntry:
    def __init__(
        self,
        train_id: str,
        station_id: str,
        scheduled_arrival_seconds: float,
        scheduled_departure_seconds: float,
        platform_id: Optional[str] = None
    ):
        self.train_id = train_id
        self.station_id = station_id
        self.scheduled_arrival = scheduled_arrival_seconds
        self.scheduled_departure = scheduled_departure_seconds
        self.platform_id = platform_id

class TimetableManager:
    def __init__(self):
        self.entries: List[TimetableEntry] = []

    def add_entry(self, entry: TimetableEntry):
        self.entries.append(entry)

    def get_schedule_for_train(self, train_id: str) -> List[TimetableEntry]:
        return [e for e in self.entries if e.train_id == train_id]

    def get_scheduled_departure(self, train_id: str, station_id: str) -> Optional[float]:
        for e in self.entries:
            if e.train_id == train_id and e.station_id == station_id:
                return e.scheduled_departure
        return None
