import os

import uvicorn

from agents.booking_agent import create_bookings_db


if __name__ == "__main__":
    if not os.path.isfile('bookings.sqlite'):
        create_bookings_db()
    uvicorn.run("backend_service:app", host='0.0.0.0', port=8000)
