import streamlit as st
import requests
import json
import os
import logging
from sqlalchemy.orm import Session
from database import get_db, init_db
from models import Conversation, Messages
import PyPDF2
import docx

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for PPLX_KEY environment variable
if 'PPLX_KEY' not in os.environ:
    logger.warning("PPLX_KEY environment variable not found. Please set it before making API calls.")
    st.warning("⚠️ PPLX_KEY environment variable not found. Please set it before making API calls.")

# Initialize the database (run this once when starting your app)
init_db()

os.makedirs("uploads", exist_ok=True)  # Create 'uploads' directory if it doesn't exist
os.makedirs("contents", exist_ok=True)  # Create 'contents' directory if it doesn't exist

# Function to create a new conversation
def create_initial_conversation():
    db = next(get_db())
    if not db.query(Conversation).first():
        new_conversation = Conversation(name="Initial Conversation")
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        logger.info(f"Created initial conversation: {new_conversation.id}")
        return new_conversation
    return None

# Function to add a new conversation
def add_conversation(name):
    db = next(get_db())
    new_conversation = Conversation(name=name)
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    logger.info(f"Added new conversation: {new_conversation.id}")
    return new_conversation

# Function to add a new message
def add_message(conversation_id, role, content):
    db = next(get_db())
    message_data = {"role": role, "content": content}
    new_message = Messages(conversation_id=conversation_id, data=json.dumps(message_data))
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    logger.info(f"Added new message to conversation {conversation_id}")
    return new_message

# Function to get all conversations
def get_conversations():
    db = next(get_db())
    conversations = db.query(Conversation).all()
    logger.info(f"Retrieved {len(conversations)} conversations")
    return conversations

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
            logger.error(f"Error decoding JSON for message ID {msg.id}: {msg.data}")
    logger.info(f"Retrieved {len(result)} messages for conversation {conversation_id}")
    return result

# Function to delete a conversation
def delete_conversation(conversation_id):
    db = next(get_db())
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        db.query(Messages).filter(Messages.conversation_id == conversation_id).delete()
        db.delete(conversation)
        db.commit()
        logger.info(f"Deleted conversation: {conversation_id}")
        return True
    logger.warning(f"Conversation not found: {conversation_id}")
    return False

# Function to save the uploaded file
def save_uploaded_file(uploaded_file):
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    logger.info(f"Saved uploaded file: {file_path}")
    return file_path

# Function to download a text file with user-provided content
def create_downloadable_text_file(content, filename="download.txt"):
    with open(filename, "w") as f:
        f.write(content)
    logger.info(f"Created downloadable file: {filename}")
    return filename

def list_files_in_directory(directory):
    """Returns a list of filenames in the given directory."""
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        logger.info(f"Listed {len(files)} files in {directory}")
        return files
    except FileNotFoundError:
        logger.error(f"Directory not found: {directory}")
        return []

# Function to call Perplexity API
def call_perplexity_api(prompt):
    api_key = os.environ.get('PPLX_KEY')
    if not api_key:
        return "PPLX_KEY environment variable not found. Please set it before making API calls."

    api_url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "llama-3.1-sonar-huge-128k-online",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logger.error(f"Error calling Perplexity API: {str(e)}")
        return f"Sorry, I couldn't generate a response. Error: {str(e)}"

# New function to read and process the uploaded document
def process_document(file_path):
    _, file_extension = os.path.splitext(file_path)
    content = ""

    try:
        if file_extension.lower() == '.pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text()
        elif file_extension.lower() in ['.docx', '.doc']:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                content += para.text + "\n"
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        logger.info(f"Processed document: {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error processing document {file_path}: {str(e)}")
        return f"Error processing document: {str(e)}"

# Modified function to map content to selected 5C categories with separate API calls and yield results one by one
def map_to_5c(content, selected_categories):
    categories = {
        "Character": ("""
        Analyze the provided project document, focusing on the Character aspect for credit scoring. Evaluate the following elements:
        1. Years in operation
        2. Industry reputation
        3. Management experience
        4. Regulatory compliance history
        
        Scoring (0-5 scale):
        0 - Poor reputation, multiple regulatory issues
        1 - Some concerns, minor regulatory issues
        2 - Average reputation, no major issues
        3 - Good reputation, strong compliance
        4 - Excellent reputation, industry leader
        5 - Outstanding reputation, exemplary track record
        
        Provide a concise analysis addressing each element above. If any information is missing, note its absence. Conclude with:
        1. An overall Character assessment summary
        2. A Character score on a scale of 0-100
        3. Brief recommendations for improvement or areas needing clarification
        Base your analysis solely on the document's content. Maintain objectivity and a professional tone throughout your response.
        """),
        "Capacity": ("""
        Analyze the provided project document, focusing on the Capacity aspect for credit scoring. Evaluate the following elements:
        1. Debt-to-equity ratio
        2. Operating cash flow
        3. Profit margins
        4. Revenue growth rate
        
        Scoring (0-5 scale):
        0 - Severe financial distress
        1 - Struggling financially
        2 - Average financial performance
        3 - Strong financial position
        4 - Very strong financials
        5 - Exceptional financial health
        
        Provide a brief analysis for each element above. If any information is missing, note its absence. Conclude with:
        1. An overall Capacity assessment summary
        2. A Capacity score on a scale of 0-100
        3. Key recommendations for enhancing project capacity
        Base your analysis solely on the document's content. Maintain objectivity and a professional tone throughout your response.
        """),
        "Capital": ("""
        Analyze the provided project document, focusing on the Capital aspect for credit scoring. Evaluate the following elements:
        1. Total assets
        2. Net worth
        3. Liquidity ratio
        4. Capital adequacy ratio (for financial institutions)
        
        Scoring (0-5 scale):
        0 - Severely undercapitalized
        1 - Undercapitalized
        2 - Adequately capitalized
        3 - Well-capitalized
        4 - Very well-capitalized
        5 - Exceptionally strong capital position
        
        Provide a brief analysis for each element above. If any information is missing, note its absence. Conclude with:
        1. An overall Capital assessment summary
        2. A Capital score on a scale of 0-100
        3. Recommendations for improving capital position or structure
        Base your analysis solely on the document's content. Maintain objectivity and a professional tone throughout your response.
        """),
        "Collateral": ("""
        Analyze the provided project document, focusing on the Collateral aspect for credit scoring. Evaluate the following elements:
        1. Quality of assets
        2. Diversification of asset portfolio
        3. Valuation of assets
        4. Ease of liquidation
        
        Scoring (0-5 scale):
        0 - No viable collateral
        1 - Limited, low-quality collateral
        2 - Adequate collateral
        3 - Good quality, diversified collateral
        4 - High-quality, easily liquidated collateral
        5 - Premium collateral or strong guarantees
        
        Provide a brief analysis for each element above. If any information is missing, note its absence. Conclude with:
        1. An overall Collateral assessment summary
        2. A Collateral score on a scale of 0-100
        3. Recommendations for improving collateral quality or coverage
        Base your analysis solely on the document's content. Maintain objectivity and a professional tone throughout your response.
        """),
        "Conditions": ("""
        Analyze the provided project document, focusing on the Conditions aspect for credit scoring. Evaluate the following elements:
        1. Economic conditions in customer's primary markets
        2. Industry trends
        3. Geopolitical risks
        4. Natural disaster exposure
        
        Scoring (0-5 scale):
        0 - Extremely unfavorable conditions
        1 - Challenging conditions
        2 - Neutral conditions
        3 - Favorable conditions
        4 - Very favorable conditions
        5 - Optimal conditions for growth and stability
        
        Provide a brief analysis for each element above. If any information is missing, note its absence. Conclude with:
        1. An overall Conditions assessment summary
        2. A Conditions score on a scale of 0-100
        3. Recommendations for addressing unfavorable conditions or leveraging positive ones
        Base your analysis solely on the document's content. Maintain objectivity and a professional tone throughout your response.
        """)
    }
    
    results = {}
    for category in selected_categories:
        description = categories[category]
        prompt = f"""
        Analyze the following content focusing on the {category} aspect of the 5C method:

        {content}

        {category}: {description}

        Provide key points and insights based on the given content.
        """
        result = call_perplexity_api(prompt)
        results[category] = result
        yield category, result
    
    # Store the complete 5C analysis results in the session state
    st.session_state['5c_analysis'] = results
    
    logger.info("Completed selected 5C analysis and stored in session state")

# Create an initial conversation if none exists
create_initial_conversation()

# Streamlit app
st.title("REALM: Reinsurance Eval Analysis for Megaprojects")

# Sidebar for page selection
st.sidebar.header("Navigation")
page = st.sidebar.radio("Page", ["Risk Assessment", "Download Sample"])

if page == "Download Sample":
    st.header("Download Sample Report")

    # List and provide downloadable files from 'contents' folder
    st.subheader("Available Files for Download")
    
    files = list_files_in_directory("contents")
    
    if files:
        for file in files:
            file_path = os.path.join("contents", file)
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"Download {file}",
                    data=f,
                    file_name=file,
                    mime="text/plain"
                )
    else:
        st.info("No files available for download.")

elif page == "Risk Assessment":
    st.header("Risk Assessment Page")
    
    # Sidebar for managing conversations
    st.sidebar.header("Conversations")
    
    # Display the list of conversations
    conversations = get_conversations()
    
    # Create a new conversation
    def create_new_conversation():
        if new_conversation_name:
            new_conv = add_conversation(new_conversation_name)
            st.session_state['selected_conversation'] = new_conv
            st.session_state['messages'] = []
            st.session_state['file_processed'] = False
            st.session_state['5c_analysis'] = None
            st.rerun()

    new_conversation_name = st.sidebar.text_input("New Conversation Name", key="new_conv_name", on_change=create_new_conversation)

    # Select conversation
    selected_conversation = st.sidebar.selectbox(
        "Select a conversation",
        options=conversations,
        format_func=lambda x: x.name,
        key="conversation_selector"
    )

    if selected_conversation:
        st.session_state['selected_conversation'] = selected_conversation
        st.session_state['messages'] = get_messages(selected_conversation.id)

        # Add delete button for the selected conversation
        if st.sidebar.button(f"Delete '{selected_conversation.name}'"):
            if delete_conversation(selected_conversation.id):
                st.sidebar.success(f"Conversation '{selected_conversation.name}' deleted.")
                del st.session_state['selected_conversation']
                del st.session_state['messages']
                st.session_state['file_processed'] = False
                st.session_state['5c_analysis'] = None
                st.rerun()
            else:
                st.sidebar.error("Failed to delete the conversation.")

    # File upload at the start of each conversation
    if not st.session_state.get('file_processed', False):
        st.write("Please upload a file to start the conversation.")
        uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])
        
        if uploaded_file is not None:
            # Add checkboxes for selecting which C's to analyze
            st.write("Select which aspects to analyze:")
            selected_categories = []
            cols = st.columns(5)
            categories = ["Character", "Capacity", "Capital", "Collateral", "Conditions"]
            
            for i, category in enumerate(categories):
                if cols[i].checkbox(category, value=True):
                    selected_categories.append(category)
            
            if st.button("Start Analysis", disabled=len(selected_categories) == 0):
                if len(selected_categories) == 0:
                    st.warning("Please select at least one category to analyze.")
                else:
                    file_path = save_uploaded_file(uploaded_file)
                    content = process_document(file_path)
                    st.write("Analyzing document...")
                    
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    
                    # Add the analysis to the conversation as bot messages one by one
                    if st.session_state.get('selected_conversation'):
                        for i, (category, result) in enumerate(map_to_5c(content, selected_categories)):
                            message = f"Here's the {category} analysis:\n\n{result}"
                            add_message(st.session_state['selected_conversation'].id, "assistant", message)
                            st.session_state['messages'].append({"role": "assistant", "content": message})
                            
                            # Update the progress bar based on selected categories
                            progress = (i + 1) / len(selected_categories)
                            progress_bar.progress(progress)
                            
                            # Display the message
                            st.chat_message("assistant").write(message)
                    
                    st.session_state['file_processed'] = True
                    st.rerun()

    # Display messages from the conversation
    if st.session_state.get('selected_conversation'):
        for msg in st.session_state["messages"]:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                if msg["role"] == "user":
                    st.chat_message("user").write(msg["content"])
                elif msg["role"] == "assistant":
                    st.chat_message("assistant").write(msg["content"])
            else:
                logger.warning(f"Unexpected message format: {msg}")

    # Handle new message input
    if prompt := st.chat_input("Type your message here..."):
        # Append the user's message to the session state
        st.session_state["messages"].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Generate a response using the Perplexity API with 5C analysis context
        response_prompt = f"""
        Based on the 5C analysis provided earlier:

        {json.dumps(st.session_state.get('5c_analysis', {}), indent=2)}

        And the user's question:

        User: {prompt}

        Provide a detailed and informative answer, incorporating relevant aspects from the 5C analysis where applicable.
        """
        with st.spinner("Generating response..."):
            msg = call_perplexity_api(response_prompt)

        # Append the assistant's message to the session state
        st.session_state["messages"].append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

        # Save the new messages to the database
        if st.session_state.get('selected_conversation'):
            add_message(st.session_state['selected_conversation'].id, "user", prompt)
            add_message(st.session_state['selected_conversation'].id, "assistant", msg)

        st.rerun()

logger.info("App finished running")
