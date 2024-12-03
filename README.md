 
# 🌟 AI-Powered Python Content Generator

![AI-Powered-Python-Content-Generator](AI-Powered-Python-Content-Generator.gif)  
**Website**: [AI-Powered Python Content Generator](https://ai-powered-python-content-generator.streamlit.app/)


**Use Firefox** [![Firefox Icon](https://firefox-dev.tools/photon/images/product-identity-assets/firefox.png)](https://www.mozilla.org/en-US/firefox/new/) because Chrome does not display PDFs properly in Streamlit apps. For more information, see this discussion: [link](https://discuss.streamlit.io/t/problems-displaying-pdf-in-streamlit-cloud/35555).

---

## 🚀 Overview
The **AI-Powered Python Content Generator** is a tool designed to assist students and educators. You can input any query or Python concept, and HugChat will generate notes in PDF format, as well as Python code in a Jupyter Notebook.

### 📝 How to Use:
1. **Enter Your Query**:  
   Type your query (e.g., "Explain dictionaries in Python") in the left panel.
2. **Authenticate**:  
   Provide your HugChat credentials (Username and Password).
3. **Submit Your Query**:  
   Click **Submit** to receive a markdown response from HugChat.
4. **Edit Markdown**:  
   Modify the markdown response (if necessary) in the center panel.
5. **Generate & Preview**:  
   In the right panel, generate and preview your PDF or Jupyter Notebook. You can open the notebook in Google Colab and download them.

---

## ⚙️ Installation Instructions

### 1. **Create an Account on Hugging Face**  
- Sign up at [Hugging Face](https://huggingface.co/welcome).

### 2. **Install Anaconda**  
- Download and install **Anaconda** from [here](https://www.anaconda.com/products/distribution).
- After installation, create a new Conda environment using the provided `AdvancedProgramming.yml` file:
  ```bash
  conda env create -f LearnPythonWithAI.yml
  ```
- Once the environment is created, activate it by running:
  ```bash
  conda activate LearnPythonWithAI
  ```

### 3. **Run the Application**  
- After all dependencies are installed, run the application using:
  ```bash
  streamlit run AI-Powered-Python-Content-Generator.py
  ```
 
## 💡 Example Usage
**Query**: *"Explain dictionaries in Python"*

**Generated Notes**:  
- **Definition**: A dictionary in Python is an unordered collection of data in the form of key-value pairs.
- **Example Code**:
  ```python
  my_dict = {"name": "John", "age": 25}
  print(my_dict["name"])  # Output: John
  ```
 
