from railway_twin.simulation.timetable import TimetableManager, TimetableEntry

def test_timetable_lookup():
    tm = TimetableManager()
    e1 = TimetableEntry("T101", "ST_A", 0.0, 300.0, "P1")
    tm.add_entry(e1)

    sched = tm.get_schedule_for_train("T101")
    assert len(sched) == 1
    assert sched[0].station_id == "ST_A"

    dep = tm.get_scheduled_departure("T101", "ST_A")
    assert dep == 300.0
