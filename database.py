import pymysql

def get_db_connection():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="skillmatch123",
            database="skillmatch_db",
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f" Error connecting to MySQL: {e}")
        return None
