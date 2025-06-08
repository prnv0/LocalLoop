import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
    st.session_state.history = []

# Function to send a message to the backend
def send_message(message):
    payload = {"message": message}
    if st.session_state.session_id:
        payload["session_id"] = st.session_state.session_id
    try:
        resp = requests.post(f"{API_URL}/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        st.error(f"Error communicating with API: {e}")
        return None

    # Update session_id and history
    st.session_state.session_id = data.get("session_id", st.session_state.session_id)
    # Append bot reply
    st.session_state.history.append({
        "sender": "bot",
        "reply": data.get("reply"),
        "options": data.get("options"),
        "itinerary": data.get("itinerary")
    })
    return data

# On first load, start the conversation
if not st.session_state.history:
    initial = send_message("hi")

st.title("Trip Planner Chatbot")

# Display conversation history
for turn in st.session_state.history:
    if turn["sender"] == "bot":
        st.markdown(f"**Bot:** {turn['reply']}")
    else:
        st.markdown(f"**You:** {turn['message']}")

# Get the last bot response to determine input type
last = st.session_state.history[-1] if st.session_state.history else None

# Input handling
if last and last.get("options"):
    # Multi-select for options
    st.write("Please select your choices:")
    choices = st.multiselect("Options:", last["options"], key="choices")
    # other = st.text_input("Other (comma-separated):", key="other")
    
    if st.button("Send Selection"):
        # Combine choices and other inputs
        selection = []
        if choices:
            selection.extend(choices)
        # if other:
        #     selection.extend([o.strip() for o in other.split(",") if o.strip()])
        
        message = ", ".join(selection) if selection else "none"
        
        # Add user message to history and send
        st.session_state.history.append({"sender": "user", "message": message})
        send_message(message)
        st.rerun()
        
else:
    # Free text input
    user_input = st.text_input("Your message:", key="text_input")
    
    if st.button("Send Message") and user_input:
        st.session_state.history.append({"sender": "user", "message": user_input})
        send_message(user_input)
        st.rerun()

# Display itinerary if available
if last and last.get("itinerary"):
    st.subheader("Itinerary")
    st.json(last["itinerary"]) 