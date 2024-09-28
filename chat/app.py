import streamlit as st
import torch
from transformers import pipeline
import json
import os
from sqlalchemy.orm import Session
from database import get_db, init_db
from models import Conversation, Messages

# Define device (0 for GPU if available, otherwise -1 for CPU)
device = 0 if torch.cuda.is_available() else -1

# Load the GPT-based model (e.g., GPT-2)
model = pipeline("text-generation", model="gpt2", device=device)

# Initialize the database (run this once when starting your app)
init_db()

# Function to create a new conversation
def create_initial_conversation():
    db = next(get_db())
    if not db.query(Conversation).first():
        new_conversation = Conversation(name="Initial Conversation")
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        return new_conversation
    return None

# Function to add a new conversation
def add_conversation(name):
    db = next(get_db())
    new_conversation = Conversation(name=name)
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

# Function to add a new message
def add_message(conversation_id, role, content):
    db = next(get_db())
    message_data = {"role": role, "content": content}
    new_message = Messages(conversation_id=conversation_id, data=json.dumps(message_data))
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

# Function to get all conversations
def get_conversations():
    db = next(get_db())
    return db.query(Conversation).all()

# Function to get messages for a specific conversation
def get_messages(conversation_id):
    db = next(get_db())
    messages = db.query(Messages).filter(Messages.conversation_id == conversation_id).all()
    result = []
    for msg in messages:
        try:
            message_data = json.loads(msg.data)
            result.append(message_data)
        except json.JSONDecodeError:
            # Handle the error or log it
            print(f"Error decoding JSON for message ID {msg.id}: {msg.data}")
    return result

# Function to save the uploaded file
def save_uploaded_file(uploaded_file):
    os.makedirs("uploads", exist_ok=True)  # Create 'uploads' directory if it doesn't exist
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Create an initial conversation if none exists
create_initial_conversation()

# Streamlit UI
st.sidebar.title("Chat Application")

# Define custom CSS for the sidebar links
custom_css = """
    <style>
    .sidebar-link {
        color: #0000EE;
        text-decoration: none;
    }
    .sidebar-link:hover {
        text-decoration: underline;
    }
    </style>
"""
st.sidebar.markdown(custom_css, unsafe_allow_html=True)

# Sidebar for managing conversations
with st.sidebar:
    st.header("Conversations")
    
    # Display the list of conversations
    conversations = get_conversations()
    
    # Create a new conversation
    new_conversation_name = st.text_input("New Conversation Name")
    if st.button("Create New Conversation") and new_conversation_name:
        add_conversation(new_conversation_name)
        st.session_state['selected_conversation'] = None  # Reset selected conversation
        st.session_state['messages'] = []  # Clear messages

    for conv in conversations:
        link = f'<a class="sidebar-link" href="?id={conv.id}">{conv.name}</a>'
        st.markdown(link, unsafe_allow_html=True)

query_params = st.query_params
selected_conversation_id = query_params.get("id", [None])[0]

if selected_conversation_id:
    selected_conversation = next((conv for conv in get_conversations() if conv.id == int(selected_conversation_id)), None)
    if selected_conversation:
        st.session_state['selected_conversation'] = selected_conversation
        st.session_state['messages'] = get_messages(selected_conversation.id)
else:
    if 'selected_conversation' not in st.session_state or st.session_state['selected_conversation'] is None:
        st.session_state['selected_conversation'] = conversations[0] if conversations else None
        st.session_state['messages'] = get_messages(st.session_state['selected_conversation'].id) if st.session_state['selected_conversation'] else []

# Display messages from the conversation
if st.session_state.get('selected_conversation'):
    for msg in st.session_state["messages"]:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            st.chat_message(msg["role"]).write(msg["content"])
        else:
            # Handle unexpected message format
            print(f"Unexpected message format: {msg}")

# File upload state handling
if 'upload_requested' not in st.session_state:
    st.session_state['upload_requested'] = False

# Handle new message input
if prompt := st.chat_input():
    # Append the user's message to the session state
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Check if the user asked to upload a file
    st.session_state['upload_requested'] = "upload file" in prompt.lower()

    # If not requesting file upload, generate a response
    if not st.session_state['upload_requested']:
        # Generate a response using the model
        response = model(prompt, max_length=100, num_return_sequences=1)
        msg = response[0]['generated_text'].strip()

        # Append the assistant's message to the session state
        st.session_state["messages"].append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

        # Save the new messages to the database
        if st.session_state.get('selected_conversation'):
            add_message(st.session_state['selected_conversation'].id, "user", prompt)
            add_message(st.session_state['selected_conversation'].id, "assistant", msg)

# If file upload is requested, show the upload button
if st.session_state['upload_requested']:
    uploaded_file = st.file_uploader("Choose a file", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file is not None:
        file_path = save_uploaded_file(uploaded_file)
        uploaded_message = f"File uploaded: {uploaded_file.name}"

        # Append the file upload message to the session state
        st.session_state["messages"].append({"role": "assistant", "content": uploaded_message})
        st.chat_message("assistant").write(uploaded_message)

        # Save the upload confirmation message to the database
        if st.session_state.get('selected_conversation'):
            add_message(st.session_state['selected_conversation'].id, "assistant", uploaded_message)

        # Reset the upload request state after upload is done
        st.session_state['upload_requested'] = False
