import uuid

import requests
import streamlit as st

AGENT_API_URL = "http://localhost:8000/chat"
APP_TITLE = 'Appointment Booking Chatbot'
APP_ICON = "🛠️"


if __name__ == '__main__':
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        menu_items={},
    )
    st.title("Hi from Michelle, Your Appointment Manager")

    # Hide the streamlit upper-right chrome
    st.html(
        """
        <style>
        [data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
            }
        </style>
        """,
    )
    if st.get_option("client.toolbarMode") != "minimal":
        st.set_option("client.toolbarMode", "minimal")
        # await asyncio.sleep(0.1)
        st.rerun()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    user_input = st.chat_input("Say something...")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            response = requests.post(
                AGENT_API_URL,
                json={
                    "user_input": user_input,
                    "thread_id": st.session_state.thread_id
                },
                timeout=15
            )
            response.raise_for_status()
            bot_response = response.json()["response"]
        except Exception as e:
            bot_response = "Something went wrong. Please try again later."
            st.error(str(e))

        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)
