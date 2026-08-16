from typing import Dict, List, Any

def get_disruption_scenario() -> Dict[str, Any]:
    return {
        "name": "Block B5 Failure Scenario",
        "description": "Block B5 undergoes sudden failure at t=300s",
        "events": [
            {"time": 300.0, "type": "BLOCK_FAILURE", "target": "B5"},
            {"time": 600.0, "type": "DELAY_INJECTION", "target": "T101", "delay_min": 10.0}
        ]
    }
