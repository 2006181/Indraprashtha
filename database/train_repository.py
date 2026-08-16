from database.connection import get_connection
class TrainRepository:
    @staticmethod
    def get_all_trains():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM trains
        """)
        trains = cursor.fetchall()
        cursor.close()
        conn.close()
        return trains
