import streamlit as st
import markdown_it
import pdfkit
import base64
from io import BytesIO
from hugchat import hugchat
from hugchat.login import Login
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import nbformat
import tempfile
import re
import fitz  # PyMuPDF for PDF to text extraction
from docx import Document
import os
import hashlib
import datetime
import shutil

# Create a user directory manager
class UserDirectoryManager:
    def __init__(self, base_dir="./user_data/"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
    def get_user_directory(self, username):
        # Create a unique directory name based on username hash
        username_hash = hashlib.md5(username.encode()).hexdigest()[:10]
        user_dir = os.path.join(self.base_dir, username_hash)
        
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            # Create subdirectories for different content types
            for subdir in ['pdf', 'ipynb', 'markdown', 'docx', 'cookies']:
                os.makedirs(os.path.join(user_dir, subdir), exist_ok=True)
        
        return user_dir
    
    def get_cookies_directory(self, username):
        user_dir = self.get_user_directory(username)
        cookies_dir = os.path.join(user_dir, "cookies")
        if not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir)
        return cookies_dir
    
    def save_content(self, username, content_type, content, filename=None, query=None):
        user_dir = self.get_user_directory(username)
        
        # Get the appropriate subdirectory
        if content_type in ['pdf', 'ipynb', 'markdown', 'docx']:
            subdir = os.path.join(user_dir, content_type)
        else:
            subdir = user_dir
        
        # Create filename with timestamp if not provided
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            query_part = ""
            if query:
                # Sanitize query for filename
                query_part = "_" + "".join(c if c.isalnum() else "_" for c in query)[:30]
            
            # Set file extension
            if content_type == 'pdf':
                file_ext = ".pdf"
            elif content_type == 'ipynb':
                file_ext = ".ipynb"
            elif content_type == 'markdown':
                file_ext = ".md"
            elif content_type == 'docx':
                file_ext = ".docx"
            else:
                file_ext = ".txt"
            
            filename = f"{content_type}_{timestamp}{query_part}{file_ext}"
        else:
            # Ensure proper extension on provided filename
            ext = f".{content_type}" if content_type != 'markdown' else '.md'
            if not filename.endswith(ext):
                filename = f"{filename}{ext}"
        
        file_path = os.path.join(subdir, filename)
        
        # Save the content based on type
        if content_type in ['pdf', 'docx'] or isinstance(content, bytes):
            # Binary content
            with open(file_path, 'wb') as f:
                if isinstance(content, str):
                    f.write(content.encode('utf-8'))
                else:
                    f.write(content)
        else:
            # Text content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return file_path
    
    def get_file_history(self, username):
        user_dir = self.get_user_directory(username)
        history = {
            'pdf': [],
            'ipynb': [],
            'markdown': [],
            'docx': [],
            'other': []
        }
        
        # Collect files from each subdirectory
        for content_type in ['pdf', 'ipynb', 'markdown', 'docx']:
            subdir = os.path.join(user_dir, content_type)
            if os.path.exists(subdir):
                history[content_type] = [
                    os.path.join(subdir, f) 
                    for f in os.listdir(subdir)
                    if os.path.isfile(os.path.join(subdir, f))
                ]
        
        # Check main directory for other files
        for f in os.listdir(user_dir):
            file_path = os.path.join(user_dir, f)
            if os.path.isfile(file_path) and not any(file_path in files for files in history.values()):
                history['other'].append(file_path)
        
        # Sort files by modification time (newest first)
        for category in history:
            history[category].sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        return history
    
    def clean_old_files(self, username, days_old=30):
        user_dir = self.get_user_directory(username)
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days_old)
        cutoff_timestamp = cutoff_time.timestamp()
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(user_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Skip files in cookies directory
                if "cookies" in file_path:
                    continue
                
                # Check file modification time
                mod_time = os.path.getmtime(file_path)
                if mod_time < cutoff_timestamp:
                    os.remove(file_path)

# Create a singleton instance
user_manager = UserDirectoryManager()

# Function to convert markdown to notebook
def convert_markdown_to_notebook(markdown_text):
    """
    Converts markdown text to a Jupyter notebook structure.
    Extracts and organizes markdown and code blocks.
    """
    # Regular expression to match code blocks
    code_pattern = r"```(?:python)?(.*?)```"  # Matches both ``` and ```python
    code_blocks = []
    matches = re.finditer(code_pattern, markdown_text, re.DOTALL)
    
    # Extract all code blocks
    for match in matches:
        code_blocks.append(match.group(1))  # Do not strip leading spaces

    # Split text into sections around the code blocks
    text_sections = re.split(code_pattern, markdown_text, flags=re.DOTALL)

    # Initialize notebook structure
    notebook = nbformat.v4.new_notebook()

    # Build notebook cells
    for i, section in enumerate(text_sections):
        if i % 2 == 0:
            # Text section (markdown)
            if section.strip():  # Ignore empty sections
                notebook.cells.append(nbformat.v4.new_markdown_cell(source=section.strip()))
        else:
            # Code block
            if section.strip():
                notebook.cells.append(nbformat.v4.new_code_cell(source=section))

    return notebook

# Setup Streamlit page configuration
st.set_page_config(page_title="AI-Powered Python Content Generator", layout="wide")

# Styling for the page
st.markdown("""
    <style>
        /* Page Title Styling */
        .title {
            text-align: center;
            font-family: 'Georgia', serif;
            font-size: 40px;
            color: #2c3e50;
            padding: 30px;
        }

        /* Container styling for sections */
        .container {
            border-radius: 10px;
            border: 1px solid #ddd;
            background-color: #f4f6f9;
            padding: 20px;
            margin-bottom: 20px;
        }

        /* Header text for sections */
        .header-text {
            text-align: center;
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
        }

        /* Custom button styles */
        .stButton>button {
            background-color: #3498db;
            color: white;
            font-size: 16px;
            border-radius: 8px;
            padding: 12px 25px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Flexbox container for layout */
        .column-wrapper {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            gap: 20px;
            padding: 20px;
        }

        /* Styling the text areas and other input components */
        .stTextArea>textarea {
            font-size: 16px;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #bdc3c7;
            background-color: #ecf0f1;
            color: #2c3e50;
            width: 100%;
        }

        /* Styling the markdown editor area */
        .stAce {
            background-color: #2d3436;
            color: #dfe6e9;
            border-radius: 8px;
            padding: 10px;
        }

        /* Styling the download button */
        .stDownloadButton>button {
            background-color: #e74c3c;
            color: white;
            font-size: 16px;
            border-radius: 8px;
            padding: 12px 25px;
        }

        /* Iframe Styling for PDF preview */
        iframe {
            border-radius: 8px;
            border: 1px solid #ddd;
            margin-top: 10px;
            width: 100%;
            height: 1000px;
            overflow: auto;
        }

        /* Styling for the instruction panel */
        .instructions {
            background-color: #f9f9f9; /* Light gray background */
            padding: 20px; /* Add some padding */
            border-radius: 8px; /* Rounded corners */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Subtle shadow */
            margin-bottom: 20px; /* Space below */
        }

        /* Style for the header text */
        .instructions h2 {
            color: #2a9d8f; /* Green-blue header text */
            margin-bottom: 15px;
        }

        /* Style for the paragraphs inside the instructions */
        .instructions p {
            color: #333; /* Dark gray text */
            font-size: 1rem; /* Standard font size */
            line-height: 1.5; /* Comfortable line spacing */
        }

        /* Style for the unordered list */
        .instructions ul {
            list-style-type: disc; /* Bullet points */
            padding-left: 20px; /* Indent bullets */
        }

        /* Style for list items */
        .instructions ul li {
            margin-bottom: 10px; /* Space between items */
            font-size: 1rem; /* Standard font size */
            line-height: 1.5; /* Comfortable spacing */
            color: #555; /* Medium gray text */
        }

        /* Add hover effect for emphasis */
        .instructions ul li:hover {
            color: #e76f51; /* Highlight text on hover */
            cursor: default;
        }
    </style>
""", unsafe_allow_html=True)

# Title of the page
st.markdown('<div class="title">AI-Powered Python Content Generator 🖥️ 📄</div>', unsafe_allow_html=True)

# Instructions for the user with a professional layout
st.markdown("""
    <head>
        <!-- Load Bootstrap CSS -->
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <!-- Load Tailwind CSS -->
        <script src="https://cdn.tailwindcss.com"></script>
        <!-- Load Font Awesome CSS -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    </head>
    <div class="instructions text-center p-4">
        <h2 class="text-3xl font-bold mb-4">AI-Powered Python Content Generator</h2>
        <p class="text-lg mb-4">This tool is designed to assist students and educators in learning Python concepts. Simply input a query or concept, and HugChat will generate notes in PDF format and code in Jupyter Notebook</p>
        <ul class="list-disc list-inside text-left mx-auto max-w-lg">
            <li class="mb-2">
                <i class="fas fa-keyboard text-blue-500 mr-2"></i>
                <strong>Step 1:</strong> Enter your query (e.g., "Explain dictionaries in Python") in the left panel.
            </li>
            <li class="mb-2">
                <i class="fas fa-user-lock text-green-500 mr-2"></i>
                <strong>Step 2:</strong> Provide your HugChat credentials (Username and Password) to authenticate.
            </li>
            <li class="mb-2">
                <i class="fas fa-arrow-right text-yellow-500 mr-2"></i>
                <strong>Step 3:</strong> Click <strong>"Submit"</strong> to receive a markdown response from HugChat.
            </li>
            <li class="mb-2">
                <i class="fas fa-edit text-teal-500 mr-2"></i>
                <strong>Step 4:</strong> Edit the markdown response (if necessary) in the center panel.
            </li>
            <li class="mb-2">
                <i class="fas fa-download text-blue-500 mr-2"></i>
                <strong>Step 5:</strong> Generate and preview your PDF, Jupyter Notebook (which can be opened in <a href="https://colab.research.google.com/" target="_blank" class="text-blue-600 underline">Google Colab</a>),  in the right panel, then download them.
            </li>
        </ul>
        <p>If you need assistance, feel free to contact me on <a href="https://github.com/MuhammadMuneeb007" target="_blank" class="text-blue-600 underline"><i class="fab fa-github mr-2"></i> GitHub</a>.</p>
    </div>
""", unsafe_allow_html=True)

# Create tabs for Content Generator and User History
tab1, tab2 = st.tabs(["Content Generator", "Your History"])

with tab1:
    st.markdown("""
        <style>
            .container {
                max-width: 600px;
                max-height: 50px;
                margin: 10px auto;
                padding: 5px;
                text-align: center;
            }
            .header-text {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 8px;
            }
            .stTextInput, .stTextArea {
                width: 100%;
                margin-bottom: 8px;
            }
            .stTextArea {
                height: 100px;
            }
            .stButton {
                margin-top: 10px;
            }
        </style>
        <div class="container">
            <h3 class="header-text">User Input</h3>
        </div>
    """, unsafe_allow_html=True)
     
    # Create columns for user input, username, password, and submit button
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])  # Adjust columns size ratio

    # User enters the command/query in the first column
    with col1:
        user_input = st.text_area("Enter your query", height=68, key="user_input", label_visibility="collapsed", placeholder="e.g., 'Explain dictionaries in Python'")

    # Username input in the second column
    with col2:
        username = st.text_input("Username", max_chars=50, key="username", placeholder="Username")

    # Password input in the third column
    with col3:
        password = st.text_input("Password", type="password", max_chars=50, key="password", placeholder="Password")

    # Submit button in the fourth column
    with col4:
        submit_button = st.button("Submit", key="submit_button")
     
    # Handling the form submission and HugChat API login
    if submit_button:
        if user_input:  # Ensure query input is provided
            query = user_input
            if username and password:  # Check for both username and password
                st.session_state.authenticated = True
                st.session_state.current_username = username  # Store username in session
                
                # Create user directory and get cookies path
                cookie_path_dir = user_manager.get_cookies_directory(username)
                
                # Login to HugChat
                sign = Login(username, password)
                cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
                chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
                id = chatbot.new_conversation()
                chatbot.change_conversation(id)
                message_result = chatbot.chat(query)

                response = message_result
                st.session_state.hugchat_response = str(response)
                
                # Save the markdown response
                user_manager.save_content(username, 'markdown', str(response), query=query)
            else:
                st.error("Please provide both username and password to authenticate.")

    # Create a three-column layout
    col1, col2, col3 = st.columns([3, 3, 3])
     
    from streamlit_ace import st_ace
    # Middle pane: HugChat Response (Editable)
    with col1:
        st.markdown('<div class="container"><h3 class="header-text">Markdown Response</h3>', unsafe_allow_html=True)
        
        if 'hugchat_response' in st.session_state:
            hugchat_response = st.session_state.hugchat_response
              
            edited_markdown = st_ace(
                        value=hugchat_response,
                        language="markdown",
                        height=1000,
                        theme="monokai",
                        wrap=True,
                        show_gutter=True,
                        auto_update=True,
                    )
             
            st.session_state['edited_response'] = edited_markdown
        else:
            st.info("Enter a query and authenticate to see the response.")
        st.markdown("</div>", unsafe_allow_html=True)
     
    with col2:
        st.markdown('<div class="container"><h3 class="header-text">PDF Preview 📄</h3>', unsafe_allow_html=True)
         
        # PDF preview section
        if 'edited_response' in st.session_state and 'current_username' in st.session_state:
            # Convert the edited Markdown to HTML
            md_parser = markdown_it.MarkdownIt()
            html_content = md_parser.render(st.session_state.edited_response)

            # Customize HTML content for PDF generation
            font_family = st.selectbox("Font Family", ["Arial", "Helvetica", "Times New Roman", "Courier", "Georgia", "Verdana", "Comic Sans MS"])
            html_content = f"""
            <style>
                body {{
                    font-size: 12px;
                    font-family: '{font_family}'; 
                    color: #000000;
                    background-color: #f9f9f9;
                    margin-top: 20px;
                    margin-bottom: 20px;
                    margin-left: 20px;
                    margin-right: 20px;
                }}
            </style>
            {html_content}
            """

            # Generate PDF from HTML using pdfkit with local file access enabled
            options = {'no-images': '', 'enable-local-file-access': ''}
            pdf = pdfkit.from_string(html_content, False, options=options)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf_file:
                tmp_pdf_file.write(pdf)
                tmp_pdf_file_path = tmp_pdf_file.name

            def pdf_to_base64(pdf_path):
                with open(pdf_path, "rb") as pdf_file:
                    pdf_data = pdf_file.read()
                return base64.b64encode(pdf_data).decode("utf-8")

            # Convert PDF to base64
            pdf_base64 = pdf_to_base64(tmp_pdf_file_path)

            # Embed the PDF in an HTML tag
            pdf_html = f'''
                <embed src="data:application/pdf;base64,{pdf_base64}#view=FitH" width="100%" height="800" />
            '''

            # Display the PDF
            st.markdown(pdf_html, unsafe_allow_html=True)
            
            # Save PDF to user directory
            with open(tmp_pdf_file_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
                
            # Save the PDF to user directory
            pdf_path = user_manager.save_content(
                st.session_state.current_username, 
                'pdf', 
                pdf_data, 
                query=user_input
            )

            # Add a download button for the PDF
            st.download_button(
                label="Download PDF 📥",
                data=pdf_data, 
                file_name="hugchat_response.pdf",
                mime="application/pdf"
            )

            # Convert PDF to Word
            def pdf_to_text(pdf_file):
                doc = fitz.open(pdf_file)
                text = ""
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text += page.get_text()
                return text

            def text_to_word(text):
                document = Document()
                paragraphs = text.split("\n")
                for paragraph in paragraphs:
                    if paragraph.strip():
                        document.add_paragraph(paragraph.strip())
                return document

            # Extract text and create Word document
            pdf_file = open(tmp_pdf_file_path, 'rb')
            extracted_text = pdf_to_text(pdf_file)
            word_doc = text_to_word(extracted_text)

            # Save Word document to BytesIO
            word_file = BytesIO()
            word_doc.save(word_file)
            word_file.seek(0)
            
            # Save Word document to user directory
            word_file.seek(0)
            word_data = word_file.read()
            docx_path = user_manager.save_content(
                st.session_state.current_username, 
                'docx', 
                word_data, 
                query=user_input
            )
            
            # Reset for download button
            word_file.seek(0)

            # Add a download button for the Word file
            st.download_button(
                label="Download as Word 📥",
                data=word_file,
                file_name="hugchat_response.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.info("Authenticate and submit a query to generate PDF.")
        
    with col3:
        st.markdown('<div class="container"><h3 class="header-text">Preview and Display as Jupyter Notebook 📒</h3>', unsafe_allow_html=True)
     
        if 'edited_response' in st.session_state and 'current_username' in st.session_state:
            # Convert the markdown to a Jupyter notebook
            markdown_text = st.session_state.edited_response
            nb = convert_markdown_to_notebook(markdown_text)

            # Save the notebook to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.ipynb', mode='w', delete=False) as temp_file:
                nbformat.write(nb, temp_file)
                notebook_path = temp_file.name

            # Display the notebook content as markdown and code cells
            for cell in nb['cells']:
                if cell['cell_type'] == 'markdown':
                    st.markdown(cell['source'], unsafe_allow_html=True)
                elif cell['cell_type'] == 'code':
                    st.code(cell['source'], language='python')

            # Save notebook to user directory
            with open(notebook_path, "r") as file:
                notebook_content = file.read()
                
            ipynb_path = user_manager.save_content(
                st.session_state.current_username, 
                'ipynb', 
                notebook_content, 
                query=user_input
            )

            # Download link for the notebook
            st.markdown(f"### Download the Notebook")
            with open(notebook_path, "r") as file:
                st.download_button(
                    label="Download Notebook (.ipynb)",
                    data=file,
                    file_name="notebook.ipynb",
                    mime="application/x-ipynb+json"
                )
        else:
            st.info("Authenticate and submit a query to generate previews.")

# User History Tab
with tab2:
    if 'current_username' in st.session_state:
        username = st.session_state.current_username
        history = user_manager.get_file_history(username)
        
        st.markdown("## Your Content History")
        
        # Display PDFs
        if history['pdf']:
            with st.expander("PDF Files", expanded=True):
                for pdf_file in history['pdf'][:5]:  # Show top 5
                    file_name = os.path.basename(pdf_file)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(file_name)
                    with col2:
                        with open(pdf_file, "rb") as f:
                            st.download_button(
                                label="Download",
                                data=f,
                                file_name=file_name,
                                mime="application/pdf"
                            )
        
        # Display Notebooks
        if history['ipynb']:
            with st.expander("Jupyter Notebooks", expanded=True):
                for nb_file in history['ipynb'][:5]:  # Show top 5
                    file_name = os.path.basename(nb_file)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(file_name)
                    with col2:
                        with open(nb_file, "r") as f:
                            st.download_button(
                                label="Download",
                                data=f,
                                file_name=file_name,
                                mime="application/x-ipynb+json"
                            )
        
        # Display Markdown files
        if history['markdown']:
            with st.expander("Markdown Files", expanded=True):
                for md_file in history['markdown'][:5]:  # Show top 5
                    file_name = os.path.basename(md_file)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(file_name)
                    with col2:
                        with open(md_file, "r") as f:
                            st.download_button(
                                label="Download",
                                data=f,
                                file_name=file_name,
                                mime="text/markdown"
                            )
        
        # Display Word documents
        if history['docx']:
            with st.expander("Word Documents", expanded=True):
                for docx_file in history['docx'][:5]:  # Show top 5
                    file_name = os.path.basename(docx_file)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(file_name)
                    with col2:
                        with open(docx_file, "rb") as f:
                            st.download_button(
                                label="Download",
                                data=f,
                                file_name=file_name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                            
        # File management options
        st.markdown("## Manage Your Files")
        with st.expander("File Management"):
            days = st.slider("Clean files older than (days):", 1, 90, 30)
            if st.button("Clean old files"):
                user_manager.clean_old_files(username, days_old=days)
                st.success(f"Files older than {days} days have been removed.")
    else:
        st.info("Please log in to view your history.")
