import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="NewStrongPassword123!",
        database="railway_digital_twin"
    )

    return connection
