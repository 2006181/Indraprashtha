from ortools.sat.python import cp_model


def optimize_sequence(twin, block_id=None, horizon_minutes=30):
    model = cp_model.CpModel()

    trains = [
        t for t in twin.trains.values()
        if t.status != "ARRIVED"
        and (block_id is None or t.current_block == block_id)
    ]

    if not trains:
        return {
            "block_id": block_id or "ALL",
            "ordered_train_ids": [],
            "objective_value": 0,
            "explanation": "No active trains require sequencing."
        }

    # If trains are on different blocks, sequence all candidates by
    # priority + delay, but use CP-SAT to decide their relative order.
    n = len(trains)
    positions = {}
    for t in trains:
        positions[t.train_id] = model.NewIntVar(0, n - 1, f"pos_{t.train_id}")

    model.AddAllDifferent(list(positions.values()))

    # Cost:
    # lower position is earlier. High priority should be earlier;
    # large delays should be earlier.
    terms = []
    for t in trains:
        urgency = int(round(t.current_delay_min * 10 + t.priority * 8))
        # Penalize late positions for urgent trains.
        terms.append((n - 1 - positions[t.train_id]) * urgency)

    # Add pairwise soft preference. CP-SAT objective maximizes urgency-weighted
    # early placement.
    model.Maximize(sum(terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 2.0
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        ordered = sorted(
            trains,
            key=lambda x: (-x.priority, -x.current_delay_min)
        )
        return {
            "block_id": block_id or "ALL",
            "ordered_train_ids": [x.train_id for x in ordered],
            "objective_value": 0,
            "explanation": "Fallback priority/delay ordering used."
        }

    ordered = sorted(trains, key=lambda t: solver.Value(positions[t.train_id]))
    objective = float(solver.ObjectiveValue())

    return {
        "block_id": block_id or "ALL",
        "ordered_train_ids": [x.train_id for x in ordered],
        "objective_value": round(objective, 2),
        "explanation": (
            "Sequence prioritizes higher-priority and more-delayed trains "
            "while enforcing one unique position per train."
        )
    }