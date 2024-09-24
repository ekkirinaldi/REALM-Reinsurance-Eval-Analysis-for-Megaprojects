import streamlit as st
import tempfile
import os
import requests
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Set up API keys
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
PERPLEXITY_API_KEY = st.secrets["PERPLEXITY_API_KEY"]

# Set up Streamlit page
st.set_page_config(page_title="Document Analysis with Perplexity API")
st.title("Document Analysis using Perplexity API")

def process_file(file):
    # Get the file extension
    file_extension = os.path.splitext(file.name)[1]

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name

    # Load the document based on its type
    if file_extension == ".pdf":
        loader = PyPDFLoader(temp_file_path)
    elif file_extension == ".docx":
        loader = Docx2txtLoader(temp_file_path)
    elif file_extension == ".txt":
        loader = TextLoader(temp_file_path)
    else:
        raise ValueError("Unsupported file type")

    documents = loader.load()

    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    # Create embeddings and store in vector database
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(texts, embeddings)

    # Clean up the temporary file
    os.unlink(temp_file_path)

    return db, " ".join([doc.page_content for doc in documents])

def perplexity_search(query, content):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-sonar-huge-128k-online",
        "messages": [
            {
                "role": "system",
                "content": "Answer in JSON with format: {'Analysis': 'Your answer here', 'score': 0, summary: 'Your summary here'}. You are a helpful assistant that analyzes documents and extracts specific information based on the given query."
            },
            {
                "role": "user",
                "content": f"Given the following document content, please answer this query: {query}\n\nDocument content: {content}"
            }
        ]
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

# Initialize session state
if "processed_file" not in st.session_state:
    st.session_state.processed_file = None
    st.session_state.document_content = None

if uploaded_file is not None and st.session_state.processed_file is None:
    with st.spinner("Processing file..."):
        st.session_state.processed_file, st.session_state.document_content = process_file(uploaded_file)
    st.success("File processed successfully!")

if st.session_state.processed_file is not None:
    # Predefined queries
    categories = ["Character Assessment Analysis", "Capacity Assessment Analysis", "Capital Assessment Analysis", "Collateral Assessment Analysis", "Conditions Assessment Analysis"]
    queries = [
        """
        Analyze the provided project document, focusing on the Character aspect for credit scoring. Evaluate the following elements:
        1. Project team/company reputation
        2. Track record of completing similar projects
        3. Key personnel qualifications and experience
        4. Ethical practices and corporate social responsibility
        5. Partnerships, collaborations, and client testimonials
        6. Indicators of reliability and trustworthiness
        
        Provide a concise analysis addressing each element above. If any information is missing, note its absence. Conclude with:
        1. An overall Character assessment summary
        2. A Character score on a scale of 0-100
        3. Brief recommendations for improvement or areas needing clarification
        Base your analysis solely on the document's content. Maintain objectivity and a professional tone throughout your response.
        """,
        """
        Analyze the provided project document, focusing on the Capacity aspect for credit scoring. Evaluate the following elements:
        1. Financial resources and cash flow projections
        2. Revenue streams and income stability
        3. Debt-to-Income (DTI) ratio or equivalent financial metrics
        4. Team size and expertise relative to project scope
        5. Resource allocation and management plans
        6. Risk assessment and mitigation strategies
        
        Provide a brief analysis for each element above. If any information is missing, note its absence. Conclude with:
        1. An overall Capacity assessment summary
        2. A Capacity score on a scale of 0-100
        3. Key recommendations for enhancing project capacity
        Base your analysis solely on the document's content. Maintain objectivity and a professional tone throughout your response.
        """,
        """
        Analyze the provided project document, focusing on the Capital aspect for credit scoring. Evaluate the following elements:
        1. Initial investment or seed funding
        2. Available liquid assets and reserves
        3. Equity structure and ownership distribution
        4. Capital expenditure plans and budgets
        5. Sources of additional funding (if applicable)
        6. Asset valuation and net worth assessment
        
        Provide a brief analysis for each element above. If any information is missing, note its absence. Conclude with:
        1. An overall Capital assessment summary
        2. A Capital score on a scale of 0-100
        3. Recommendations for improving capital position or structure
        Base your analysis solely on the document's content. Maintain objectivity and a professional tone throughout your response.
        """,
        """
        Analyze the provided project document, focusing on the Collateral aspect for credit scoring. Evaluate the following elements:
        1. Identified assets offered as collateral
        2. Valuation of proposed collateral
        3. Liquidity and marketability of collateral assets
        4. Loan-to-Value (LTV) ratio, if applicable
        5. Legal status and ownership of collateral
        6. Potential risks or depreciation factors affecting collateral value
        
        Provide a brief analysis for each element above. If any information is missing, note its absence. Conclude with:
        1. An overall Collateral assessment summary
        2. A Collateral score on a scale of 0-100
        3. Recommendations for improving collateral quality or coverage
        Base your analysis solely on the document's content. Maintain objectivity and a professional tone throughout your response.
        """,
        """
        Analyze the provided project document, focusing on the Conditions aspect for credit scoring. Evaluate the following elements:
        1. Purpose and objectives of the project
        2. Market conditions and industry trends
        3. Economic factors affecting the project
        4. Regulatory environment and compliance requirements
        5. Competitive landscape and market positioning
        6. Potential external risks or opportunities
        
        Provide a brief analysis for each element above. If any information is missing, note its absence. Conclude with:
        1. An overall Conditions assessment summary
        2. A Conditions score on a scale of 0-100
        3. Recommendations for addressing unfavorable conditions or leveraging positive ones
        Base your analysis solely on the document's content. Maintain objectivity and a professional tone throughout your response.
        """
    ]

    # Display results for predefined queries
    st.header("Document Analysis Results")
    for category, query in zip(categories, queries):
        with st.expander(category):
            with st.spinner("Analyzing..."):
                result = perplexity_search(query, st.session_state.document_content)
            st.write(result)

    # Custom query input
    st.header("Ask a Custom Question")
    custom_query = st.text_input("Enter your question about the document:")
    if custom_query:
        with st.spinner("Analyzing..."):
            result = perplexity_search(custom_query, st.session_state.document_content)
        st.write(result)

    # Download processed content
    st.download_button(
        label="Download Processed Document Content",
        data=st.session_state.document_content,
        file_name="processed_document.txt",
        mime="text/plain"
    )