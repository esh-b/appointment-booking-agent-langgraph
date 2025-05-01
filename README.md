# Meet Michelle, the appointment manager assistant

This repository contains a working prototype of Michelle, an appointment management agent for Shine & Style, a local hair salon. Built using **LangGraph**, **Streamlit**, and **OpenAI** models, this project showcases a conversational assistant capable of handling salon bookings.

Please note that this a work in progress (its Version0), and serves as an early-stage prototype. The goal is to eventually evolve it into a production-ready system. The current system can currently book, reschedule and cancel appointments.

## In progress
- [X] Appointment rescheduling or cancellation features.
- [X] Decouple LangGraph agent (backend) from Streamlit (frontend); expose the backend as a containerized FastAPI endpoint.
- [ ] Answer FAQ questions about the salon timings, etc
- [ ] Allow to book with specific stylists at the salon (as is the case with certain well-known salons).
- [ ] Make SQL backend (checking availability) more efficient to handle lots of appointment requests.
- [ ] Make this a voice agent eventually for practical applications.

## Simple System Design
![Current System design](resources/system_design_v1.png)

## Get started
### 1. Install Requirements
Make sure you have Python 3.10+ installed. Then run:
```bash
pip install -r requirements.txt
```

### 2. Setup the Database
Initialize the local SQLite database by running:

```bash
python database/create_sqlite_db.py
```
This would create a new sqlite file `bookings.sqlite` in the current directory by default.

### 3. Run the Streamlit App
Launch the UI using:

```bash
streamlit run streamlit_app.py
```
The app will open in your browser at http://localhost:8501 by default.

## Disclaimer

This is a work-in-progress project and not suitable for production use yet. Features may be incomplete, and the codebase is subject to frequent changes.
