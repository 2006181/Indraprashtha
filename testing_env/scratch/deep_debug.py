import os
import sys
import math
import time
import random
import traceback

# Setup paths
sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("."))

from railway_twin.digital_twin.network import RailwayNetwork
from railway_twin.digital_twin.block import Block, BlockType, BlockState
from railway_twin.digital_twin.signal import Signal, SignalAspect
from railway_twin.digital_twin.station import Station
from railway_twin.digital_twin.platform import Platform
from railway_twin.digital_twin.train import Train, TrainType, TrainStatus
from railway_twin.digital_twin.state_manager import StateManager

from railway_twin.simulation.simulator import TrainSimulator
from railway_twin.simulation.events import SimulationEvent, EventType
from railway_twin.simulation.telemetry import TelemetryGenerator, TelemetryFrame
from railway_twin.simulation.timetable import TimetableManager, TimetableEntry

from railway_twin.ml.preprocessing import FeaturePreprocessor, RawFeatureInput
from railway_twin.ml.eta_model import ETAPredictionModel
from railway_twin.ml.delay_model import DelayPredictionModel
from railway_twin.ml.conflict_model import ConflictPredictionModel

from railway_twin.optimization.conflict_detector import ConflictDetector
from railway_twin.optimization.constraints import ConstraintEvaluator
from railway_twin.optimization.optimizer import TrafficOptimizer
from railway_twin.optimization.safety_validator import SafetyValidator

from tests.fixtures.railway_network import create_complex_network
from tests.fixtures.sample_trains import create_sample_train_fleet


def run_detailed_debug():
    print("==================================================")
    print("STARTING DETAILED SYSTEM DEBUGGING & STRESS AUDIT")
    print("==================================================")
    
    issues_found = []

    # ----------------------------------------------------
    # DEBUG CATEGORY 1: Digital Twin & State Consistency
    # ----------------------------------------------------
    print("\n--- [Category 1] Debugging Digital Twin Edge Cases ---")
    net = RailwayNetwork("Debug Section")
    b1 = Block("B1", "Block 1", length_km=1.0)
    b2 = Block("B2", "Block 2", length_km=1.0)
    net.add_block(b1)
    net.add_block(b2)
    net.connect_blocks("B1", "B2")

    t1 = Train("T1", "Express 1", route=["B1", "B2"])
    net.register_train(t1)
    sm = StateManager(net)

    # Move T1 into B1
    sm.move_train_to_block("T1", "B1")
    if b1.state != BlockState.OCCUPIED or b1.occupied_by_train_id != "T1":
        issues_found.append("Block state mismatch after initial move to B1")

    # Attempt double occupation error check
    t2 = Train("T2", "Express 2", route=["B1", "B2"])
    net.register_train(t2)
    try:
        sm.move_train_to_block("T2", "B1")
        issues_found.append("Failed to reject double occupation of B1 by T2!")
    except ValueError as e:
        print(f" [PASS] Block single occupancy rejection caught correctly: {e}")

    # Move T1 from B1 to B2
    sm.move_train_to_block("T1", "B2")
    if b1.state != BlockState.CLEAR or b1.occupied_by_train_id is not None:
        issues_found.append("Block B1 was not cleared when T1 moved to B2")
    if b2.state != BlockState.OCCUPIED or b2.occupied_by_train_id != "T1":
        issues_found.append("Block B2 was not marked OCCUPIED by T1")
    print(" [PASS] Digital Twin block transfer state transition verified.")

    # ----------------------------------------------------
    # DEBUG CATEGORY 2: Simulation Delta Jumps & Signal Sync
    # ----------------------------------------------------
    print("\n--- [Category 2] Debugging Simulator Large Step Jumps ---")
    cnet = create_complex_network()
    t_fast = Train("TFast", "Superfast", max_speed=130.0, route=[f"B{i}" for i in range(1, 10)])
    cnet.register_train(t_fast)
    sim = TrainSimulator(cnet, seed=42)

    # Large time delta step (60 seconds at 130 km/h = 2.16 km movement, traversing block length 2.5km)
    sim.step(60.0)
    print(f"  TFast position after 60s step: {t_fast.position:.3f} km, current_block: {t_fast.current_block_id}, status: {t_fast.status.value}")
    if t_fast.position < 0:
        issues_found.append("Negative train position observed after sim step")

    # Inject red signal ahead
    sig3 = cnet.signals.get("SIG_3")
    if sig3:
        sig3.set_functional(False)  # Force signal failure -> RED aspect
        print("  Injected signal failure on SIG_3 (Aspect forced to RED)")

    for _ in range(5):
        sim.step(10.0)
    print(f"  TFast position near failed signal: {t_fast.position:.3f} km, speed: {t_fast.current_speed} km/h, status: {t_fast.status.value}")

    if t_fast.current_block_id == "B3" and t_fast.current_speed > 0:
        issues_found.append("Train failed to stop before failed RED signal!")
    else:
        print(" [PASS] Train correctly brought to standstill before RED signal.")

    # ----------------------------------------------------
    # DEBUG CATEGORY 3: ML Models Fuzzing & Numerical Boundary Testing
    # ----------------------------------------------------
    print("\n--- [Category 3] Debugging ML Pipelines & Fuzzing Inputs ---")
    eta_model = ETAPredictionModel()
    delay_model = DelayPredictionModel()
    conflict_model = ConflictPredictionModel()

    fuzz_inputs = [
        RawFeatureInput(speed=0.0, distance=10.0, train_type="FREIGHT", current_delay=0.0, block_id="B1", time_of_day_seconds=0.0),
        RawFeatureInput(speed=0.0001, distance=0.0, train_type="EXPRESS", current_delay=120.0, block_id="B1", time_of_day_seconds=86400.0),
        RawFeatureInput(speed=160.0, distance=100.0, train_type="PASSENGER", current_delay=0.0, block_id="B1", time_of_day_seconds=43200.0)
    ]

    for idx, f_in in enumerate(fuzz_inputs):
        try:
            eta = eta_model.predict_eta_minutes(f_in)
            if math.isnan(eta) or math.isinf(eta) or eta < 0:
                issues_found.append(f"Fuzz test input {idx} produced invalid ETA: {eta}")
            else:
                print(f"  Fuzz input {idx} ETA prediction: {eta} min [PASS]")
        except Exception as ex:
            issues_found.append(f"Fuzz test input {idx} crashed ETA model: {ex}")

    # Delay model metrics boundary check (ss_tot == 0 edge case)
    mae, rmse, r2 = delay_model.evaluate_metrics([10.0, 10.0], [10.0, 10.0])
    if math.isnan(r2) or math.isinf(r2):
        issues_found.append(f"Zero-variance evaluation produced invalid R2: {r2}")
    else:
        print(f" [PASS] Delay model zero-variance evaluation handled safely: R2={r2}")

    # ----------------------------------------------------
    # DEBUG CATEGORY 4: Optimizer Cyclic Conflict Resolution & Hard Invariants
    # ----------------------------------------------------
    print("\n--- [Category 4] Debugging Optimizer & Safety Validation ---")
    opt_net = create_complex_network()
    validator = SafetyValidator(opt_net, min_headway_sec=180.0)
    optimizer = TrafficOptimizer(opt_net)

    # Create cyclic/triple train contention on Block B5
    fleet = create_sample_train_fleet(count=3)
    for t in fleet:
        opt_net.register_train(t)

    # All 3 trains want B5 at exact same time window 100-300s
    contention_plan = {
        "T_001": [{"block_id": "B5", "enter_time": 100.0, "exit_time": 300.0}],
        "T_002": [{"block_id": "B5", "enter_time": 100.0, "exit_time": 300.0}],
        "T_003": [{"block_id": "B5", "enter_time": 100.0, "exit_time": 300.0}]
    }

    report_before = validator.validate_plan(contention_plan)
    if report_before.is_safe:
        issues_found.append("Unsafe triple contention plan passed initial validation unexpectedly!")
    else:
        print(" [PASS] Initial triple contention plan correctly flagged as UNSAFE.")

    opt_result = optimizer.optimize(contention_plan)
    report_after = validator.validate_plan(opt_result.schedule_plan)
    
    print(f"  Optimizer Runtime: {opt_result.runtime_seconds*1000:.2f} ms")
    print(f"  Optimized Plan Safety Status: {report_after.is_safe}")
    if not report_after.is_safe:
        issues_found.append(f"Optimized triple contention plan failed safety validation! Violations: {report_after.violations}")
    else:
        print(" [PASS] Optimized plan successfully resolved contention and PASSED ALL SAFETY INVARIANTS.")

    # ----------------------------------------------------
    # SUMMARY REPORT
    # ----------------------------------------------------
    print("\n==================================================")
    print("DETAILED DEBUGGING SUMMARY RESULT")
    print("==================================================")
    if issues_found:
        print(f"CRITICAL: Found {len(issues_found)} issue(s) during deep debug:")
        for err in issues_found:
            print(f"  ❌ {err}")
    else:
        print("[OK] ALL 4 CATEGORIES PASSED DEEP DEBUGGING & HARDENING AUDIT WITH 0 ISSUES!")
    print("==================================================")

if __name__ == "__main__":
    run_detailed_debug()
