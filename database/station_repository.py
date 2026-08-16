from database.connection import get_connection
class StationRepository:
    @staticmethod
    def get_all_stations():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT
            station_code,
            station_name,
            state,
            railway_zone_code,
            latitude,
            longitude,
            is_junction
        FROM stations
        """
        cursor.execute(query)
        stations = cursor.fetchall()
        cursor.close()
        conn.close()
        return stations
