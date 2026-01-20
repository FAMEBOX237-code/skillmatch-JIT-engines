import pymysql

def get_db_connection(): 
    return pymysql.connect (
        host = 'localhost', 
        user='root',
        password='skilmatch123',
        database='skillmatch_db',
        cursorclass=pymysql.cursors.DictCursor
    )
