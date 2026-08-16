from copy import deepcopy
from dataclasses import asdict
from .network import RailwayNetwork
from .schemas import Train


class DigitalTwin:
    def __init__(self):
        self.network = RailwayNetwork()
        self.clock_minute = 0
        self.trains: dict[str, Train] = {}
        self.reset()

    def reset(self):
        self.clock_minute = 0
        self.trains = {
            "T101": Train(
                train_id="T101", train_type="EXPRESS", priority=5,
                origin="S1", destination="S6", current_block="B01",
                next_block="B02", speed_kmph=82, max_speed_kmph=120,
                scheduled_arrival_min=50, scheduled_departure_min=5,
                current_delay_min=0, distance_to_station_km=4.5
            ),
            "T102": Train(
                train_id="T102", train_type="PASSENGER", priority=3,
                origin="S1", destination="S6", current_block="B02",
                next_block="B03", speed_kmph=62, max_speed_kmph=100,
                scheduled_arrival_min=65, scheduled_departure_min=8,
                current_delay_min=3, distance_to_station_km=6.0
            ),
            "F201": Train(
                train_id="F201", train_type="FREIGHT", priority=1,
                origin="S1", destination="S6", current_block="B03",
                next_block="B04", speed_kmph=45, max_speed_kmph=70,
                scheduled_arrival_min=90, scheduled_departure_min=10,
                current_delay_min=6, distance_to_station_km=5.0
            ),
            "T103": Train(
                train_id="T103", train_type="LOCAL", priority=2,
                origin="S1", destination="S6", current_block="B04",
                next_block="B05", speed_kmph=55, max_speed_kmph=90,
                scheduled_arrival_min=110, scheduled_departure_min=12,
                current_delay_min=2, distance_to_station_km=7.0
            ),
            "T104": Train(
                train_id="T104", train_type="EXPRESS", priority=5,
                origin="S1", destination="S6", current_block="B05",
                next_block=None, speed_kmph=70, max_speed_kmph=120,
                scheduled_arrival_min=130, scheduled_departure_min=15,
                current_delay_min=4, distance_to_station_km=3.0
            ),
        }
        self._sync_occupancy()

    def _sync_occupancy(self):
        for block in self.network.blocks.values():
            block.occupied_by = None
        for train in self.trains.values():
            if train.status == "RUNNING" and train.current_block in self.network.blocks:
                self.network.blocks[train.current_block].occupied_by = train.train_id

    def add_train(self, train: Train):
        self.trains[train.train_id] = train
        self._sync_occupancy()

    def state(self):
        return {
            "clock_minute": self.clock_minute,
            "trains": [t.model_dump() for t in self.trains.values()],
            "blocks": [asdict(b) for b in self.network.blocks.values()],
        }

    def metrics(self):
        active = [t for t in self.trains.values() if t.status != "ARRIVED"]
        if not active:
            return {
                "clock_minute": self.clock_minute,
                "active_trains": 0,
                "average_delay_min": 0,
                "section_utilization_pct": 0,
                "conflicts": 0,
            }

        avg_delay = sum(t.current_delay_min for t in active) / len(active)
        occupied = sum(
            1 for b in self.network.blocks.values() if b.occupied_by is not None
        )
        utilization = occupied / max(len(self.network.blocks), 1) * 100

        conflicts = 0
        seen = {}
        for t in active:
            seen.setdefault(t.current_block, []).append(t.train_id)
        conflicts = sum(max(0, len(v) - 1) for v in seen.values())

        return {
            "clock_minute": self.clock_minute,
            "active_trains": len(active),
            "average_delay_min": round(avg_delay, 2),
            "section_utilization_pct": round(utilization, 2),
            "conflicts": conflicts,
        }

    def step(self, minutes: int = 1):
        for _ in range(minutes):
            self.clock_minute += 1
            self._advance_one_minute()
        return self.state()

    def _advance_one_minute(self):
        # Simple discrete-time prototype:
        # distance traveled = speed * 1/60 hour.
        # A train moves to the next block only when its remaining distance is <= 0.
        for train in self.trains.values():
            if train.status == "ARRIVED":
                continue

            block = self.network.blocks.get(train.current_block)
            if not block:
                continue

            # Safe occupancy rule for the prototype:
            # if the next block is occupied, hold the train.
            next_id = train.next_block or self.network.next_block(train.current_block)
            next_block = self.network.blocks.get(next_id) if next_id else None

            if train.distance_to_station_km <= 0.05:
                if next_block and next_block.occupied_by not in (None, train.train_id):
                    train.status = "WAITING"
                    train.current_delay_min += 1
                    continue

                if next_block:
                    train.current_block = next_block.block_id
                    train.next_block = self.network.next_block(next_block.block_id)
                    train.distance_to_station_km = next_block.length_km
                    train.status = "RUNNING"
                else:
                    train.status = "ARRIVED"
                    continue

            if train.status == "WAITING":
                if next_block and next_block.occupied_by is None:
                    train.status = "RUNNING"
                else:
                    train.current_delay_min += 1
                    continue

            effective_speed = min(train.speed_kmph, block.speed_limit_kmph)
            train.distance_to_station_km -= effective_speed / 60.0

            expected_progress = effective_speed / 60.0
            if expected_progress <= 0:
                train.current_delay_min += 1

            # Mild stochastic/operational delay propagation is intentionally
            # deterministic enough for repeatable hackathon demos.
            if self.clock_minute % 17 == 0 and train.train_type == "FREIGHT":
                train.current_delay_min += 0.2

        self._sync_occupancy()

    def clone(self):
        return deepcopy(self)