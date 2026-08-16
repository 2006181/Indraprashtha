from typing import List
from railway_twin.digital_twin.train import Train, TrainType

def create_sample_train_fleet(count: int = 10) -> List[Train]:
    fleet = []
    types = [TrainType.EXPRESS, TrainType.PASSENGER, TrainType.FREIGHT]
    for i in range(1, count + 1):
        ttype = types[(i - 1) % 3]
        max_sp = 130.0 if ttype == TrainType.EXPRESS else (100.0 if ttype == TrainType.PASSENGER else 75.0)
        prio = 10 if ttype == TrainType.EXPRESS else (6 if ttype == TrainType.PASSENGER else 3)
        route = [f"B{j}" for j in range(1, 11)]
        t = Train(
            train_id=f"T_{i:03d}",
            name=f"Train Service {i}",
            train_type=ttype,
            max_speed=max_sp,
            priority=prio,
            route=route
        )
        fleet.append(t)
    return fleet
