import uuid

import streamlit as st

from app.agents.booking_agent import booking_agent_graph


if __name__ == '__main__':
    st.set_page_config(page_title="Mechanic Chatbot", page_icon="🛠️")
    st.title("🛠️ Mechanic Appointment Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = uuid.uuid4()

    user_input = st.chat_input("Say something...")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        result = booking_agent_graph.invoke(
            {"messages": [{'role': 'user', 'content': user_input}]},
            config={'configurable': {'thread_id': st.session_state.thread_id}}
        )
        bot_response = result["messages"][-1].content

        print(booking_agent_graph.get_state({'configurable': {'thread_id': st.session_state.thread_id}})[0])

        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)
