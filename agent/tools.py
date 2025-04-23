import datetime
import pytz

from langchain_core.tools import tool
import parsedatetime

from database.db_utils import add_booking, is_slot_available, is_valid_timeslot


@tool
def convert_relative_to_absolute_datetime(text: str, current_datetime: datetime) -> str | None:
    """
    Converts a natural language date and time string into an absolute ISO 8601 datetime string.

    Args:
        text (str): A natural language expression with date and time (e.g., "next Wednesday at 4pm").
        current_datetime (datetime): A timezone-aware datetime object to use as the reference point.

    Returns:
        str | None: An ISO 8601 formatted datetime string if successful, otherwise None.
    """
    current_datetime = datetime.datetime.fromisoformat(current_datetime)
    if current_datetime.tzinfo is None:
        raise ValueError("current_datetime must be timezone-aware")

    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(text, current_datetime.timetuple())

    if parse_status == 0:
        return

    naive_dt = datetime.datetime(*time_struct[:6])
    tz = current_datetime.tzinfo

    # Localize if not timezone-aware
    if naive_dt.tzinfo is None:
        aware_dt = tz.localize(naive_dt) if hasattr(tz, 'localize') else naive_dt.replace(tzinfo=tz)
    else:
        aware_dt = naive_dt.astimezone(tz)

    return aware_dt.isoformat()


@tool
def check_availability(appointment_start_dt: str) -> dict:
    """
    Checks whether the given appointment start datetime is available for booking.

    Args:
        appointment_start_dt (str): ISO 8601 datetime string with timezone.

    Returns:
        dict: {
            'status': 'available' | 'unavailable',
            'reason': str (optional if unavailable)
        }
    """
    is_valid, reason = is_valid_timeslot(appointment_start_dt)
    if not is_valid:
        return {'status': 'error', 'reason': reason}

    if not is_slot_available(appointment_start_dt):
        return {'status': 'unavailable', 'reason': 'The requested timeslot is not available'}

    return {'status': 'available'}


@tool
def book_appointment(appointment_start_dt: str, user_name: str, user_phone_number: str):
    """
    Books an appointment for a user at the specified date and time.

    Args:
        appointment_start_dt (str): The appointment start datetime in ISO 8601 format WITH TIMEZONE (same timezone as current datetime)
            (e.g., '2025-04-23T16:00:00-04:00').
        user_name (str): The name of the user booking the appointment.
        user_phone_number (str): The user's phone number for contact or confirmation.

        dict: A dictionary containing:
            - 'status' (str): 'success' if booking was successful, 'failure' otherwise.
            - 'booking_id' (str, optional): The unique ID of the booking if successful.
            - 'reason' (str, optional): The reason for the failure.

    Raises:
        ValueError: If the appointment datetime is not in valid ISO 8601 format or is in the past.
    """

    valid_dt, failure_reason = is_valid_timeslot(appointment_start_dt)
    if valid_dt:
        if is_slot_available(appointment_start_dt):
            booking_id = add_booking(appointment_start_dt, user_name, user_phone_number)
            if booking_id:
                return {'status': 'success', 'booking_id': booking_id}
            else:
                return {'status': 'failure', 'reason': 'Internal error'}
        else:
            return {'status': 'failure', 'reason': 'The requested timeslot is no longer available'}
    else:
        return {'status': 'failure', 'reason': failure_reason}
