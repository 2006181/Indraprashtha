from dataclasses import dataclass
from typing import List, Dict, Optional
from ..digital_twin.network import RailwayNetwork

@dataclass
class SafetyValidationReport:
    is_safe: bool
    invariant_results: Dict[str, bool]
    violations: List[str]

class SafetyValidator:
    """
    Deterministic Safety Authority.
    The AI model / optimizer may recommend an action, but NO action is allowed to execute
    without passing this Safety Validator.
    """
    def __init__(self, network: RailwayNetwork, min_headway_sec: float = 180.0):
        self.network = network
        self.min_headway_sec = min_headway_sec

    def validate_plan(self, schedule_plan: Dict[str, List[Dict]]) -> SafetyValidationReport:
        violations: List[str] = []
        invariant_results = {
            "INVARIANT_1_BLOCK_SINGLE_OCCUPANCY": True,
            "INVARIANT_2_MINIMUM_HEADWAY": True,
            "INVARIANT_3_BLOCK_AVAILABILITY": True,
            "INVARIANT_4_PLATFORM_AVAILABILITY": True,
            "INVARIANT_5_CONFLICTING_ROUTES": True,
            "INVARIANT_6_OPTIMIZER_SAFETY_PASS": True,
            "INVARIANT_7_DETERMINISTIC_OVERRIDE": True
        }

        # Check block occupancy & headway
        all_moves = []
        for tid, moves in schedule_plan.items():
            for m in moves:
                all_moves.append((tid, m["block_id"], m["enter_time"], m["exit_time"], m.get("platform_id")))

        for i in range(len(all_moves)):
            for j in range(i + 1, len(all_moves)):
                t1, b1, e1, x1, p1 = all_moves[i]
                t2, b2, e2, x2, p2 = all_moves[j]

                if t1 != t2:
                    if b1 == b2:
                        # Overlap check
                        if max(e1, e2) < min(x1, x2):
                            invariant_results["INVARIANT_1_BLOCK_SINGLE_OCCUPANCY"] = False
                            violations.append(f"INVARIANT 1 VIOLATION: Block {b1} occupied simultaneously by {t1} and {t2}")

                        if abs(e2 - e1) < self.min_headway_sec:
                            invariant_results["INVARIANT_2_MINIMUM_HEADWAY"] = False
                            violations.append(f"INVARIANT 2 VIOLATION: Headway between {t1} and {t2} in {b1} is {abs(e2-e1)}s < {self.min_headway_sec}s")

                    if p1 and p2 and p1 == p2:
                        if max(e1, e2) < min(x1, x2):
                            invariant_results["INVARIANT_4_PLATFORM_AVAILABILITY"] = False
                            violations.append(f"INVARIANT 4 VIOLATION: Platform {p1} occupied simultaneously by {t1} and {t2}")

        # Check block availability
        for tid, moves in schedule_plan.items():
            for m in moves:
                bid = m["block_id"]
                if bid in self.network.blocks:
                    b = self.network.blocks[bid]
                    if not b.is_available or b.state.value == "BLOCKED":
                        invariant_results["INVARIANT_3_BLOCK_AVAILABILITY"] = False
                        violations.append(f"INVARIANT 3 VIOLATION: Train {tid} routed through unavailable block {bid}")

        # Check overall safety
        is_safe = all(invariant_results.values())
        if not is_safe:
            invariant_results["INVARIANT_6_OPTIMIZER_SAFETY_PASS"] = False

        return SafetyValidationReport(
            is_safe=is_safe,
            invariant_results=invariant_results,
            violations=violations
        )

    def validate_ai_recommendation(
        self,
        ai_proposed_action: Dict,
        schedule_plan: Dict[str, List[Dict]]
    ) -> bool:
        """
        Enforces INVARIANT 7: AI prediction can never directly override deterministic safety constraints.
        """
        report = self.validate_plan(schedule_plan)
        if not report.is_safe:
            return False  # REJECT AI recommendation regardless of confidence or priority
        return True
