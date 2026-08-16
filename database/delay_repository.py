from database.connection import get_connection

class DelayRepository:
    @staticmethod
    def get_delay(train_number):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT *
        FROM train_delays
        WHERE train_number=%s
        """
        cursor.execute(query, (train_number,))
        delay = cursor.fetchone()
        cursor.close()
        conn.close()
        return delay
