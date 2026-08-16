from railway_twin.simulation.timetable import TimetableManager, TimetableEntry

def create_sample_timetable() -> TimetableManager:
    tm = TimetableManager()
    tm.add_entry(TimetableEntry("T101", "ST_A", 0.0, 300.0, "P1"))
    tm.add_entry(TimetableEntry("T101", "ST_B", 1800.0, 2100.0, "P3"))
    tm.add_entry(TimetableEntry("T102", "ST_A", 600.0, 900.0, "P2"))
    tm.add_entry(TimetableEntry("T102", "ST_B", 2400.0, 2700.0, "P3"))
    return tm
