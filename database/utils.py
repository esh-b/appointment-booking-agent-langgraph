import sqlite3
import datetime
import uuid
import pytz

import pandas as pd

DB_PATH = './bookings.sqlite'
BOOKING_SLOT_DURATION_HRS = 1
SLOT_AVAILABLE_QUERY = """
    SELECT * FROM Bookings
    WHERE start_datetime < ?
      AND end_datetime > ?
      AND status != 'cancelled'
"""
ADD_CUSTOMER_QUERY = """
INSERT INTO Customer (id, name, phone_number, email, created_at)
VALUES (?, ?, ?, ?, ?);
"""
ADD_BOOKING_QUERY = """
    INSERT INTO Bookings (
        id, customer, start_datetime, end_datetime, booking_reason, created_at
    ) VALUES (?, ?, ?, ?, ?, ?);
"""
GET_USER_QUERY = """
    SELECT * FROM Customer
    WHERE phone_number = ?
"""
GET_ACTIVE_BOOKINGS_USER_QUERY = """
    SELECT * FROM Bookings
    WHERE customer = ? AND status = 'scheduled'
"""
GET_ACTIVE_BOOKING_BY_ID_QUERY = """
    SELECT * FROM Bookings
    WHERE id = ?
    AND status = 'scheduled'
"""
CANCEL_BOOKING_QUERY = """
    UPDATE Bookings
    SET status = 'cancelled'
    WHERE id = ?
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
    end_dt_utc = (start_dt_utc + datetime.timedelta(hours=BOOKING_SLOT_DURATION_HRS))

    with sqlite3.connect(DB_PATH) as conn:
        available_slots_df = pd.read_sql_query(
            sql=SLOT_AVAILABLE_QUERY,
            conn=conn,
            params=(end_dt_utc.isoformat(), start_dt_utc.isoformat()))
        return available_slots_df.empty


def add_customer( 
        cursor, 
        user_name: str, 
        user_phone_number: str, 
        user_email: str = None) -> str:
    customer_id = str(uuid.uuid4())
    current_dt = datetime.datetime.now(pytz.utc)

    try:
        cursor.execute(
            ADD_CUSTOMER_QUERY, 
            (
                customer_id,
                user_name,
                user_phone_number,
                user_email,
                current_dt.isoformat()
            )
        )
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
    end_dt_utc = start_dt_utc + datetime.timedelta(hours=BOOKING_SLOT_DURATION_HRS)
    current_dt = datetime.datetime.now(pytz.utc)

    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("BEGIN transaction;")
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM Customer WHERE phone_number = ?", (user_phone_number,))
            result = cursor.fetchone()
            customer_id = result[0] if result is not None else add_customer(cursor, user_name, user_phone_number)

            cursor.execute(
                ADD_BOOKING_QUERY, 
                (
                    booking_id,
                    customer_id,
                    start_dt_utc.isoformat(),
                    end_dt_utc.isoformat(),
                    booking_reason,
                    current_dt.isoformat()
                )
            )
            conn.commit()
            return booking_id
        except Exception as e:
            conn.rollback()
            print(f"Unexpected error while adding customer: {e}")


def get_active_bookings_user(user_phone_number: str) -> []:
    with sqlite3.connect(DB_PATH) as conn:
        customer_df = pd.read_sql_query(GET_USER_QUERY, conn, params=(user_phone_number,))
        if customer_df.empty:
            print('There is no customer with the provided phone number and consequently, no appointments')
            return []

        bookings_df = pd.read_sql_query(GET_ACTIVE_BOOKINGS_USER_QUERY, conn, params=(customer_df.loc[0, 'id'],))
        if bookings_df.empty:
            print('There are no active bookings for the customer')
            return
        return bookings_df[['id', 'start_datetime', 'end_datetime']].to_dict(orient='records')


def reschedule_booking(booking_id, user_phone_number, updated_start_dt_str):
    start_dt_utc = datetime.datetime.fromisoformat(updated_start_dt_str).astimezone(pytz.utc)
    end_dt_utc = start_dt_utc + datetime.timedelta(hours=BOOKING_SLOT_DURATION_HRS)
    current_dt = datetime.datetime.now(pytz.utc)
    new_booking_id = str(uuid.uuid4())

    with sqlite3.connect(DB_PATH) as conn:
        try:
            booking_df = pd.read_sql_query(GET_ACTIVE_BOOKING_BY_ID_QUERY, conn, params=(booking_id,))
            if booking_df.empty:
                print('Booking not found')
                return

            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("BEGIN transaction;")
            cursor = conn.cursor()

            result = cursor.execute(CANCEL_BOOKING_QUERY, (booking_id,))
            if result.rowcount < 1:
                print('The booking with the provided ID was not found and hence, not cancelled')
                return

            cursor.execute(
                ADD_BOOKING_QUERY, 
                (
                    new_booking_id, 
                    booking_df.loc[0, 'customer'],
                    start_dt_utc.isoformat(),
                    end_dt_utc.isoformat(),
                    booking_df.loc[0, 'booking_reason'], 
                    current_dt.isoformat()
                )
            )
            conn.commit()
            return new_booking_id
        except Exception as e:
            conn.rollback()
            print(f"Unexpected error while adding customer: {e}")


def cancel_booking(booking_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cursor = conn.cursor()

            result = cursor.execute(CANCEL_BOOKING_QUERY, (booking_id,))
            if result.rowcount < 1:
                print("No booking found with that ID. Nothing was deleted.")
                return False
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print('Unexpected error', e)
            return False


# if __name__ == '__main__':
#     booking_id = add_booking('2025-04-23T08:00:00-04:00', 'Vishwa', '6479999999')
#     print(booking_id)
#     result = is_slot_available('2025-04-23T09:00:00-04:00')
#     print(result)
