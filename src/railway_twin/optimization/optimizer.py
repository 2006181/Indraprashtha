import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from ..digital_twin.network import RailwayNetwork
from .conflict_detector import ConflictDetector, DetectedConflict
from .constraints import ConstraintEvaluator

@dataclass
class OptimizationStrategy:
    strategy_id: str
    action_type: str  # "HOLD_LOWER_PRIORITY", "REROUTE_LOOP", "SPEED_ADJUSTMENT"
    affected_train_id: str
    action_details: Dict[str, Any]

@dataclass
class OptimizationResult:
    is_valid: bool
    strategies: List[OptimizationStrategy]
    total_delay_seconds: float
    runtime_seconds: float
    schedule_plan: Dict[str, List[Dict]]
    objective_score: float

class TrafficOptimizer:
    def __init__(self, network: RailwayNetwork):
        self.network = network
        self.conflict_detector = ConflictDetector(network)
        self.constraint_evaluator = ConstraintEvaluator(network)

    def optimize(self, train_trajectories: Dict[str, List[Dict]]) -> OptimizationResult:
        start_time = time.time()
        
        # 1. Format trajectories for conflict detector
        formatted_traj = {}
        for tid, moves in train_trajectories.items():
            formatted_traj[tid] = [(m["block_id"], m["enter_time"], m["exit_time"]) for m in moves]

        conflicts = self.conflict_detector.detect_conflicts(formatted_traj)
        
        strategies: List[OptimizationStrategy] = []
        modified_plan = {tid: [dict(m) for m in moves] for tid, moves in train_trajectories.items()}

        # Resolve conflicts greedily based on train priority
        for c in conflicts:
            t1 = self.network.trains.get(c.train_id_1)
            t2 = self.network.trains.get(c.train_id_2)

            p1 = t1.priority if t1 else 5
            p2 = t2.priority if t2 else 5

            # Hold train with lower priority
            lower_train_id = c.train_id_2 if p1 >= p2 else c.train_id_1
            higher_train_id = c.train_id_1 if p1 >= p2 else c.train_id_2

            hold_time = (c.time_window_end - c.time_window_start) + 180.0
            
            # Apply shift to lower priority train's schedule
            for m in modified_plan[lower_train_id]:
                if m["block_id"] == c.resource_id:
                    m["enter_time"] += hold_time
                    m["exit_time"] += hold_time

            strategies.append(OptimizationStrategy(
                strategy_id=f"OPT-{len(strategies)+1}",
                action_type="HOLD_LOWER_PRIORITY",
                affected_train_id=lower_train_id,
                action_details={
                    "held_for_train": higher_train_id,
                    "hold_duration_sec": hold_time,
                    "at_resource": c.resource_id
                }
            ))

        # Check hard constraints on modified plan
        violations = self.constraint_evaluator.evaluate_schedule_plan(modified_plan)
        is_valid = len(violations) == 0

        total_delay = sum(
            max(0.0, m["exit_time"] - orig_m["exit_time"])
            for tid, moves in modified_plan.items()
            for m, orig_m in zip(moves, train_trajectories[tid])
        )
        
        runtime = time.time() - start_time
        objective_score = total_delay * 1.0 + (0.0 if is_valid else 10000.0)

        return OptimizationResult(
            is_valid=is_valid,
            strategies=strategies,
            total_delay_seconds=total_delay,
            runtime_seconds=runtime,
            schedule_plan=modified_plan,
            objective_score=objective_score
        )
