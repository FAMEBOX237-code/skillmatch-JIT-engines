import pymysql

def get_db_connection(): 
    return pymysql.connect (
        host = 'localhost', 
        user='root',
        password='Brenda@ictu2024',
        database='skillmatch_db',
        cursorclass=pymysql.cursors.DictCursor
    )
