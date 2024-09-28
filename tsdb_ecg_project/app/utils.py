import os
import psycopg2

def connect_to_db():
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB', 'ecg_data'),
        user=os.environ.get('POSTGRES_USER', 'your_username'),
        password=os.environ.get('POSTGRES_PASSWORD', 'your_password'),
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=5432
    )
    return conn
