import streamlit as st
import markdown_it
import pdfkit
import base64
from io import BytesIO
from hugchat import hugchat
from hugchat.login import Login
import streamlit as st
 
# Setup Streamlit page configuration
st.set_page_config(page_title="AI-Powered Python Content Generator", layout="wide")

# Right pane: PPTX and PDF Preview and Customization
# Right pane: PPTX and PDF Preview and Customization
import streamlit as st
import nbformat
from io import BytesIO
import tempfile
import streamlit as st
import nbformat
from io import BytesIO
import tempfile
import re
import re
import nbformat
import tempfile
import streamlit as st
import re
import nbformat
import tempfile
import streamlit as st

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




st.markdown("""
    <style>
        .container {
            max-width: 600px;
            max-height: 50px;
            margin: 10px auto; /* Corrected the margin */
            padding: 5px;
            text-align: center; /* Centers the content inside */
        }
        .header-text {
            font-size: 20px;  /* Reduced font size */
            font-weight: bold;
            margin-bottom: 8px;  /* Reduced bottom margin */
        }
        .stTextInput, .stTextArea {
            width: 100%;  /* Full width of the container */
            margin-bottom: 8px;  /* Reduced bottom margin */
        }
        .stTextArea {
            height: 100px;  /* Reduced height of the text area */
        }
        .stButton {
            margin-top: 10px;
        }
    </style>
    <div class="container">
        <h3 class="header-text">User Input</h3>
    </div>
""", unsafe_allow_html=True)
 
import streamlit as st

  
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
            cookie_path_dir = "./cookies/"  # Path to store cookies
            sign = Login(username, password)  # Assuming Login is a custom function for authentication
            cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)  # Simulate login
            chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # Initialize chatbot with cookies
            id = chatbot.new_conversation()
            chatbot.change_conversation(id)  # Change to the new conversation
            message_result = chatbot.chat(query)  # Send the query to HugChat API

            response = message_result
            st.session_state.hugchat_response = str(response)  # Store the response in session state
        else:
            st.error("Please provide both username and password to authenticate.")


# Create a three-column layout with flexbox for better control
col1, col2, col3  = st.columns([3,3,3 ])

 
from streamlit_ace import st_ace
# Middle pane: HugChat Response (Editable)
with col1:
    st.markdown('<div class="container"><h3 class="header-text">Markdown Response</h3>', unsafe_allow_html=True)
    
    if 'hugchat_response' in st.session_state:
        hugchat_response = st.session_state.hugchat_response
          
        #edited_markdown = st.text_area("Edit your markdown response", hugchat_response, height=1000)
        edited_markdown = st_ace(
                    value=hugchat_response,  # Initial content for the editor
                    language="markdown",     # Set to markdown mode
                    height=1000,             # Set the editor height
                    theme="monokai",         # Set theme
                    wrap=True,               # Enable wrapping of lines
                    show_gutter=True,
                 
                    auto_update=True,
                     
                )
         
        st.session_state['edited_response'] = edited_markdown  # Update the edited response

        # Save the edited response to session state
        #st.session_state.edited_response = edited_markdown
        
    else:
        st.info("Enter a query and authenticate to see the response.")
    #st.session_state.edited_response = edited_markdown
    st.markdown("</div>", unsafe_allow_html=True)  # Close container div
 
with col2:
    st.markdown('<div class="container"><h3 class="header-text">PDF Preview 📄</h3>', unsafe_allow_html=True)
     
    # PDF preview section
    if 'edited_response' in st.session_state:
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
            @import url('https://fonts.googleapis.com/css2?family={font_family.replace(" ", "+")}:wght@400;700&display=swap');
        </style>
        {html_content}
        """

        # Generate PDF from HTML using pdfkit with local file access enabled
        options = {'no-images': '', 'enable-local-file-access': ''}
        pdf = pdfkit.from_string(html_content, False, options=options)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf_file:
                tmp_pdf_file.write(pdf)
                tmp_pdf_file_path = tmp_pdf_file.name  # Get the path of the temporary file
        
        # Save the PDF to a BytesIO object
        pdf_file = BytesIO(pdf)
        pdf_file.seek(0)  # Reset pointer to the beginning of the file

        # Embed the PDF preview in an iframe with "fit to page" scaling
        pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        pdf_url = f"data:application/pdf;base64,{pdf_base64}#view=FitH"
        st.markdown(
            f'''
            <iframe 
                src="{pdf_url}" 
                width="100%" 
                height="1000px" 
                style="border: none;"
            >
            </iframe>
            ''',
            unsafe_allow_html=True
        )

        # Add a download button for the PDF
        st.download_button(
            label="Download PDF 📥",
            data=pdf_file,
            file_name="hugchat_response.pdf",
            mime="application/pdf"
        )
        import base64
        import io
        import markdown_it
        import pdfkit
        import fitz  # PyMuPDF for PDF to text extraction
        from docx import Document
        import streamlit as st
        from io import BytesIO

        def pdf_to_text(pdf_file):
            # Read the PDF using PyMuPDF
            doc = fitz.open(pdf_file)
            text = ""
            
            # Extract text from each page of the PDF
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            return text

        # Convert extracted text from PDF to Word (.docx) format
        def text_to_word(text):
            document = Document()
            # Add the extracted text as paragraphs
            paragraphs = text.split("\n")
            for paragraph in paragraphs:
                if paragraph.strip():  # Avoid adding empty paragraphs
                    document.add_paragraph(paragraph.strip())
            return document

        # Extract text from the generated PDF
        pdf_file = open(tmp_pdf_file_path, 'rb')
        extracted_text = pdf_to_text(pdf_file)

        # Generate Word document from the extracted text
        word_doc = text_to_word(extracted_text)

        # Save the Word document to a BytesIO object
        word_file = BytesIO()
        word_doc.save(word_file)
        word_file.seek(0)  # Reset pointer to the beginning of the file

        # Add a download button for the Word file
        st.download_button(
            label="Download as Word 📥",
            data=word_file,
            file_name="hugchat_response.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.markdown("</div>", unsafe_allow_html=True)  # Close container div

    else:
        st.info("Authenticate and submit a query to generate PDF.")
    
 

with col3:
    st.markdown('<div class="container"><h3 class="header-text">Preview and Display as Jupyter Notebook 📒</h3>', unsafe_allow_html=True)
 

    if 'edited_response' in st.session_state:
        # Convert the markdown to a Jupyter notebook
        markdown_text = st.session_state.edited_response  # Assuming this contains your markdown content
        nb = convert_markdown_to_notebook(markdown_text)

        # Save the notebook to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.ipynb', mode='w', delete=False) as temp_file:
            nbformat.write(nb, temp_file)
            notebook_path = temp_file.name

        # Display the notebook content as markdown and code cells in Streamlit
        for cell in nb['cells']:
            if cell['cell_type'] == 'markdown':
                st.markdown(cell['source'], unsafe_allow_html=True)  # Render markdown content
            elif cell['cell_type'] == 'code':
                st.code(cell['source'], language='python')  # Render code block

        # Provide a download link for the notebook
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


 



