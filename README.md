# Meet Michelle, the appointment manager assistant

This repository contains a working prototype of Michelle, an appointment management agent for Shine & Style, a local hair salon.

Built using LangGraph, Streamlit, and OpenAI models, this project showcases a conversational assistant capable of handling salon bookings.

Please note that this a work in progress (its V0), and serves as an early-stage prototype. The goal is to eventually evolve it into a production-ready system.


## Project structure
```bash
├── LICENSE
├── README.md
├── agent/                    ← Core Langgraph agent logic
│   ├── __init__.py
│   ├── booking_agent.py
│   ├── prompts.py
│   └── tools.py
├── database/                 ← Scripts to create and interact with the DB
│   ├── __init__.py
│   ├── create_sqlite_db.py
│   └── db_utils.py
├── requirements.txt
├── resources/                ← Assets
└── streamlit_app.py          ← Main entry point for the application
```

## Get started
1. Install Requirements

Make sure you have Python 3.10+ installed. Then run:
```bash
pip install -r requirements.txt
```

2. Setup the Database
Initialize the local SQLite database by running:
```bash
python database/create_sqlite_db.py
```

3. Run the Streamlit App
Launch the UI using:
```bash
streamlit run streamlit_app.py
```
The app will open in your browser at http://localhost:8501 by default.

## ⚠️ Disclaimer

This is a work-in-progress project and not suitable for production use yet. Expect bugs, incomplete features, and frequent changes.
