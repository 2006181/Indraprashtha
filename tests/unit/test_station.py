import pytest
from railway_twin.digital_twin.station import Station
from railway_twin.digital_twin.platform import Platform

def test_station_platform_allocation():
    st = Station("ST1", "Delhi Jn", "DLI")
    p1 = Platform("P1", "ST1", "Platform 1")
    p2 = Platform("P2", "ST1", "Platform 2")
    st.add_platform(p1)
    st.add_platform(p2)

    # Request platform for train T101
    assigned = st.request_platform("T101", preferred_platform_id="P1")
    assert assigned == "P1"
    assert p1.is_occupied is True

    # Request preferred P1 for train T102 -> should assign alternative P2
    assigned2 = st.request_platform("T102", preferred_platform_id="P1")
    assert assigned2 == "P2"
    assert p2.is_occupied is True

    # Request platform for train T103 when full -> None returned
    assigned3 = st.request_platform("T103")
    assert assigned3 is None

def test_platform_release():
    st = Station("ST1", "Delhi Jn", "DLI")
    p1 = Platform("P1", "ST1", "Platform 1")
    st.add_platform(p1)
    st.request_platform("T101", "P1")
    
    released = st.release_platform("P1", "T101")
    assert released is True
    assert p1.is_occupied is False
