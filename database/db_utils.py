import sqlite3
import datetime
import uuid
import pytz

DB_PATH = './bookings.sqlite'
SLOT_AVAILABLE_QUERY = """
    SELECT * FROM Bookings
    WHERE start_datetime < ?
      AND end_datetime > ?
"""
ADD_CUSTOMER_QUERY = """
INSERT INTO Customer (id, name, phone_number, email, created_at)
VALUES (?, ?, ?, ?, ?);
"""
ADD_BOOKING_QUERY = """
    INSERT INTO Bookings (
        id, customer_id, start_datetime, end_datetime, booking_reason, created_at
    ) VALUES (?, ?, ?, ?, ?, ?);
"""
GET_USER_QUERY = """
    SELECT * FROM Customer
    WHERE user_phone_number = ?
"""
GET_ACTIVE_BOOKINGS_USER_QUERY = """
    SELECT * FROM Bookings
    WHERE customer_id = ? AND status = 'scheduled'
"""


def is_valid_timeslot(appointment_start_dt: str) -> tuple[bool, str | None]:
    """Check if the provided appointment datetime is valid"""

    try:
        start_dt = datetime.datetime.fromisoformat(appointment_start_dt)
    except Exception as e:
        return False, "Invalid datetime format. Must be ISO 8601 with timezone."
    else:
        if start_dt.tzinfo is None:
            return False, "The appointment_start_dt must include timezone info."

    curr_dt = datetime.datetime.now(start_dt.tzinfo)
    if start_dt <= curr_dt:
        return False, 'The requested timeslot is in the past'
    return True, None


def is_slot_available(start_iso: str, DB_PATH=DB_PATH) -> bool:
    """
    Check if a slot is available by ensuring there are no overlapping appointments.
    
    Parameters:
        start_iso (str): Start datetime in ISO 8601 format (e.g., '2025-04-22 14:00:00')
    
    Returns:
        bool: True if the slot is available, False otherwise
    """
    start_dt_utc = datetime.datetime.fromisoformat(start_iso).astimezone(pytz.utc)
    end_dt_utc = (start_dt_utc + datetime.timedelta(hours=1))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(SLOT_AVAILABLE_QUERY, (end_dt_utc.isoformat(), start_dt_utc.isoformat()))
        return cursor.fetchone() is None


def add_customer(
        conn, 
        cursor, 
        user_name: str, 
        user_phone_number: str, 
        user_email: str = None) -> str:
    customer_id = str(uuid.uuid4())
    current_dt = datetime.datetime.now(pytz.utc)

    try:
        cursor.execute(ADD_CUSTOMER_QUERY, (customer_id, user_name, user_phone_number, user_email, current_dt.isoformat()))
        return customer_id
    except Exception as e:
        print(f"Unexpected error while adding customer: {e}")
        raise


def add_booking(
        start_dt_str: str,
        user_name: str,
        user_phone_number: str,
        user_email: str = None,
        booking_reason: str = None) -> str:
    booking_id = str(uuid.uuid4())
    start_dt_utc = datetime.datetime.fromisoformat(start_dt_str).astimezone(pytz.utc)
    end_dt_utc = start_dt_utc + datetime.timedelta(hours=1)
    current_dt = datetime.datetime.now(pytz.utc)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("BEGIN transaction;")
            cursor = conn.cursor()

            cursor.execute("SELECT customer_id FROM Customer WHERE phone_number = ?", (user_phone_number,))
            result = cursor.fetchone()
            customer_id = result[0] if result else add_customer(conn, cursor, user_name, user_phone_number)

            cursor.execute(ADD_BOOKING_QUERY, (booking_id, customer_id, start_dt_utc.isoformat(), end_dt_utc.isoformat(), booking_reason, current_dt.isoformat()))
            conn.commit()
            return booking_id
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error while adding customer: {e}")


def get_active_bookings_user(user_phone_number: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        cursor.execute(GET_USER_QUERY, (user_phone_number))
        customer = cursor.fetchone()

        if customer is None:
            print('There is no customer with the provided phone number and consequently, no appointments')
            return

        cursor.execute(GET_ACTIVE_BOOKINGS_USER_QUERY, (customer[0]['id']))
        customer_bookings = cursor.fetchall()
        if customer_bookings is None:
            print('There are no active bookings for the customer')
            return

        return customer_bookings

# if __name__ == '__main__':
#     booking_id = add_booking('2025-04-23T08:00:00-04:00', 'Vishwa', '6479999999')
#     print(booking_id)
#     result = is_slot_available('2025-04-23T09:00:00-04:00')
#     print(result)
