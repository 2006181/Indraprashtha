from .twin import DigitalTwin


def snapshot_metrics(twin):
    return twin.metrics()


def run_scenario(
    base_twin: DigitalTwin,
    train_id: str,
    delay_minutes: float,
    horizon_minutes: int,
):
    if train_id not in base_twin.trains:
        raise ValueError(f"Unknown train_id: {train_id}")

    baseline = base_twin.clone()
    scenario = base_twin.clone()

    scenario.trains[train_id].current_delay_min += delay_minutes

    baseline.step(horizon_minutes)
    scenario.step(horizon_minutes)

    base_m = baseline.metrics()
    scenario_m = scenario.metrics()

    delay_delta = scenario_m["average_delay_min"] - base_m["average_delay_min"]
    throughput_base = sum(
        1 for t in baseline.trains.values() if t.status == "ARRIVED"
    )
    throughput_scenario = sum(
        1 for t in scenario.trains.values() if t.status == "ARRIVED"
    )

    return {
        "baseline": {
            "metrics": base_m,
            "arrived_trains": throughput_base,
        },
        "scenario": {
            "metrics": scenario_m,
            "arrived_trains": throughput_scenario,
            "injected_delay": delay_minutes,
            "affected_train": train_id,
        },
        "improvement": {
            "average_delay_change_min": round(delay_delta, 2),
            "throughput_change": throughput_scenario - throughput_base,
            "note": (
                "Positive average-delay change means the disruption caused "
                "additional delay."
            ),
        },
    }