from database.connection import get_connection
class RouteRepository:
    @staticmethod
    def get_all_routes():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT *
        FROM train_routes
        ORDER BY train_number, stop_number
        """
        cursor.execute(query)
        routes = cursor.fetchall()
        cursor.close()
        conn.close()
        return routes
