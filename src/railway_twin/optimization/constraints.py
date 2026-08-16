from dataclasses import dataclass
from typing import List, Dict, Optional
from ..digital_twin.network import RailwayNetwork

@dataclass
class HardConstraintViolation:
    constraint_name: str
    description: str
    affected_entities: List[str]

class ConstraintEvaluator:
    def __init__(self, network: RailwayNetwork, min_headway_sec: float = 180.0):
        self.network = network
        self.min_headway_sec = min_headway_sec

    def evaluate_schedule_plan(self, schedule_plan: Dict[str, List[Dict]]) -> List[HardConstraintViolation]:
        """
        schedule_plan: dict of train_id -> list of dicts: {"block_id": str, "enter_time": float, "exit_time": float, "platform_id": Optional[str]}
        """
        violations: List[HardConstraintViolation] = []

        # 1. Single Block Occupancy & Headway
        all_movements = []
        for tid, movements in schedule_plan.items():
            for m in movements:
                all_movements.append((tid, m["block_id"], m["enter_time"], m["exit_time"], m.get("platform_id")))

        for i in range(len(all_movements)):
            for j in range(i + 1, len(all_movements)):
                t1, b1, e1, x1, p1 = all_movements[i]
                t2, b2, e2, x2, p2 = all_movements[j]

                if t1 == t2:
                    continue

                if b1 == b2:
                    # Check block overlap
                    if max(e1, e2) < min(x1, x2):
                        violations.append(HardConstraintViolation(
                            constraint_name="SINGLE_BLOCK_OCCUPANCY",
                            description=f"Trains {t1} and {t2} both occupy block {b1} simultaneously.",
                            affected_entities=[t1, t2, b1]
                        ))
                    elif abs(e2 - e1) < self.min_headway_sec:
                        violations.append(HardConstraintViolation(
                            constraint_name="MINIMUM_HEADWAY",
                            description=f"Headway between {t1} and {t2} in block {b1} is {abs(e2-e1)}s < {self.min_headway_sec}s.",
                            affected_entities=[t1, t2, b1]
                        ))

                if p1 and p2 and p1 == p2:
                    if max(e1, e2) < min(x1, x2):
                        violations.append(HardConstraintViolation(
                            constraint_name="PLATFORM_CAPACITY",
                            description=f"Trains {t1} and {t2} occupy same platform {p1} simultaneously.",
                            affected_entities=[t1, t2, p1]
                        ))

        # 2. Infrastructure Availability
        for tid, movements in schedule_plan.items():
            for m in movements:
                bid = m["block_id"]
                if bid in self.network.blocks:
                    b = self.network.blocks[bid]
                    if not b.is_available or b.state.value == "BLOCKED":
                        violations.append(HardConstraintViolation(
                            constraint_name="BLOCK_AVAILABILITY",
                            description=f"Train {tid} is assigned to unavailable/blocked block {bid}.",
                            affected_entities=[tid, bid]
                        ))

        return violations
