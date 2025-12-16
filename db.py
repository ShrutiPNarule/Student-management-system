import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="@shrutipn1410",
        dbname="college"
    )
    return conn