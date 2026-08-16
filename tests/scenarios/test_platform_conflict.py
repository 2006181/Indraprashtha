import pytest
from railway_twin.digital_twin.station import Station
from railway_twin.digital_twin.platform import Platform

def test_scenario_platform_conflict_resolution(sample_network):
    st = sample_network.stations["ST_A"]
    
    # Train 1 occupies Platform P1
    allocated_1 = st.request_platform("T101", preferred_platform_id="P1")
    assert allocated_1 == "P1"

    # Train 2 requests Platform P1 -> Should be allocated alternative P2
    allocated_2 = st.request_platform("T102", preferred_platform_id="P1")
    assert allocated_2 == "P2"
    assert allocated_2 != allocated_1
