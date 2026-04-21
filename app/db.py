import os, psycopg

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg.connect(
        DATABASE_URL, autocommit=True, row_factory=psycopg.rows.dict_row
    )


def create_schema():
    with get_conn() as conn, conn.cursor() as cur:
        # Create the schema
        cur.execute(
            """
            CREATE EXTENSION IF NOT EXISTS pgcrypto;

            CREATE TABLE IF NOT EXISTS rooms(
                id SERIAL PRIMARY KEY, 
                room_number INT NOT NULL,
                room_type VARCHAR NOT NULL,
                price NUMERIC NOT NULL,
                created_at TIMESTAMP DEFAULT now()
            );
            CREATE TABLE IF NOT EXISTS guests(
                id SERIAL PRIMARY KEY, 
                firstname VARCHAR NOT NULL,
                lastname VARCHAR NOT NULL,
                address VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT now()
            );
            CREATE TABLE IF NOT EXISTS bookings(
                id SERIAL PRIMARY KEY, 
                guest_id INT REFERENCES guests(id),
                room_id INT REFERENCES rooms(id),
                date_from DATE NOT NULL,
                date_to DATE NOT NULL,
                addinfo VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIME
            );
            
            ALTER TABLE guests ADD COLUMN IF NOT EXISTS api_key VARCHAR DEFAULT encode(gen_random_bytes(32), 'hex');
        """
        )
        # add columns
