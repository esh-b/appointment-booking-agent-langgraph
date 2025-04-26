import sqlite3
import datetime
import uuid
import pytz

DB_NAME = "bookings.sqlite"


def create_bookings_db(db_name=DB_NAME):
    """Creates and initializes the SQLite bookings database."""
    with sqlite3.connect(db_name) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        # Create Customer table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customer (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                email TEXT,
                created_at DATETIME NOT NULL
            );
        """)

        # Create Bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Bookings (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                start_datetime DATETIME NOT NULL,
                end_datetime DATETIME NOT NULL,
                booking_reason TEXT,
                status TEXT DEFAULT 'scheduled',
                created_at DATETIME NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
                UNIQUE (start_datetime, end_datetime)
            );
        """)

        # Indexes for efficient slot searching
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_booking_time 
        ON Bookings (start_datetime, end_datetime);
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_customer_phone 
        ON Customer (phone_number);
        """)

        conn.commit()
        print(f"Database '{db_name}' created with all tables and indexes.")


if __name__ == "__main__":
    create_bookings_db()
