import time
import pytest
from railway_twin.simulation.simulator import TrainSimulator
from tests.fixtures.sample_trains import create_sample_train_fleet

def test_simulation_speed_scaling(sample_network):
    train_counts = [10, 25, 50]
    benchmarks = {}

    for count in train_counts:
        # Create fresh network
        from tests.fixtures.railway_network import create_complex_network
        net = create_complex_network()
        fleet = create_sample_train_fleet(count=count)
        for t in fleet:
            net.register_train(t)

        sim = TrainSimulator(net, seed=42)

        start = time.time()
        for _ in range(50):
            sim.step(10.0)
        elapsed = time.time() - start
        
        events_processed = len(sim.history)
        events_per_sec = events_processed / elapsed if elapsed > 0 else 0.0
        benchmarks[count] = events_per_sec

        # Benchmark threshold: Must exceed 500 events/second
        assert elapsed < 5.0, f"Simulation with {count} trains took {elapsed:.2f}s (too slow)"

    print(f"\nSimulation Speed Benchmarks (Events/Sec): {benchmarks}")
