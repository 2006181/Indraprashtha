from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from ..digital_twin.network import RailwayNetwork

@dataclass
class DetectedConflict:
    conflict_type: str  # "BLOCK_OCCUPANCY", "HEADWAY_VIOLATION", "PLATFORM_OCCUPANCY", "CROSSING_ROUTE"
    train_id_1: str
    train_id_2: str
    resource_id: str  # block_id or platform_id
    time_window_start: float
    time_window_end: float

class ConflictDetector:
    def __init__(self, network: RailwayNetwork, min_headway_seconds: float = 180.0):
        self.network = network
        self.min_headway = min_headway_seconds

    def detect_conflicts(self, train_trajectories: Dict[str, List[Tuple[str, float, float]]]) -> List[DetectedConflict]:
        """
        train_trajectories: dict of train_id -> list of (block_id, enter_time, exit_time)
        """
        conflicts: List[DetectedConflict] = []
        train_ids = list(train_trajectories.keys())

        for i in range(len(train_ids)):
            for j in range(i + 1, len(train_ids)):
                t1, t2 = train_ids[i], train_ids[j]
                traj1, traj2 = train_trajectories[t1], train_trajectories[t2]

                for item1 in traj1:
                    b1 = item1["block_id"] if isinstance(item1, dict) else item1[0]
                    enter1 = item1["enter_time"] if isinstance(item1, dict) else item1[1]
                    exit1 = item1["exit_time"] if isinstance(item1, dict) else item1[2]

                    for item2 in traj2:
                        b2 = item2["block_id"] if isinstance(item2, dict) else item2[0]
                        enter2 = item2["enter_time"] if isinstance(item2, dict) else item2[1]
                        exit2 = item2["exit_time"] if isinstance(item2, dict) else item2[2]

                        if b1 == b2:
                            # Overlapping block occupancy time window
                            overlap_start = max(enter1, enter2)
                            overlap_end = min(exit1, exit2)

                            if overlap_start < overlap_end:
                                conflicts.append(DetectedConflict(
                                    conflict_type="BLOCK_OCCUPANCY",
                                    train_id_1=t1,
                                    train_id_2=t2,
                                    resource_id=b1,
                                    time_window_start=overlap_start,
                                    time_window_end=overlap_end
                                ))
                            elif abs(enter2 - enter1) < self.min_headway:
                                conflicts.append(DetectedConflict(
                                    conflict_type="HEADWAY_VIOLATION",
                                    train_id_1=t1,
                                    train_id_2=t2,
                                    resource_id=b1,
                                    time_window_start=min(enter1, enter2),
                                    time_window_end=max(enter1, enter2)
                                ))
        return conflicts
