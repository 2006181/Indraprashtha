from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class Block:
    block_id: str
    from_station: str
    to_station: str
    length_km: float
    speed_limit_kmph: float
    occupied_by: str | None = None


@dataclass
class Station:
    station_id: str
    name: str
    platforms: int


class RailwayNetwork:
    def __init__(self):
        self.stations: Dict[str, Station] = {}
        self.blocks: Dict[str, Block] = {}
        self._build_default()

    def _build_default(self):
        station_data = [
            ("S1", "Alpha", 2),
            ("S2", "Bravo", 3),
            ("S3", "Central", 3),
            ("S4", "Delta", 2),
            ("S5", "Echo", 2),
            ("S6", "Foxtrot", 2),
        ]
        for sid, name, platforms in station_data:
            self.stations[sid] = Station(sid, name, platforms)

        block_data = [
            ("B01", "S1", "S2", 8.0, 100),
            ("B02", "S2", "S3", 10.0, 90),
            ("B03", "S3", "S4", 7.0, 80),
            ("B04", "S4", "S5", 12.0, 100),
            ("B05", "S5", "S6", 9.0, 90),
        ]
        for bid, a, b, km, limit in block_data:
            self.blocks[bid] = Block(bid, a, b, km, limit)

    def to_dict(self):
        return {
            "stations": [asdict(x) for x in self.stations.values()],
            "blocks": [asdict(x) for x in self.blocks.values()],
        }

    def next_block(self, block_id: str):
        ids = list(self.blocks.keys())
        try:
            i = ids.index(block_id)
        except ValueError:
            return None
        return ids[i + 1] if i + 1 < len(ids) else None

    def block_for_route(self, station_index: int):
        ids = list(self.blocks.keys())
        if 0 <= station_index < len(ids):
            return ids[station_index]
        return None