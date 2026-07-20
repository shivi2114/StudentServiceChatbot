import streamlit as st
from chatbot import get_response

st.set_page_config(
    page_title="AI Student Services Chatbot",
    page_icon="",
    layout="wide"
)

st.title(" AI Student Services Chatbot")

st.write("Welcome! Ask me anything about student services.")

# Sidebar
st.sidebar.title("Student Services")

st.sidebar.write("""
- Admission
- Hostel
- Fees
- Library
- Scholarship
- Placement
- Transport
- Timetable
- Attendance
- Examination
""")

if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Ask your question...")

if prompt:

    st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt
        }
    )

    with st.chat_message("user"):
        st.write(prompt)

    response = get_response(prompt)

    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":response
        }
    )

    with st.chat_message("assistant"):
        st.write(response)

st.markdown("---")

st.caption("Made using Python • Machine Learning • Streamlit")