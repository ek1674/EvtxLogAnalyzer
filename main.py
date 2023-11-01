#  This is a beta LLM for NLP, needs to be trained on a custom database THIS SECTION NEEDS TO BE UPDATED
#  Time spent on this == 37 hours

# Import necessary libraries
import spacy  # Imports the spaCy library, used for natural language processing (NLP).
#import spacy_transformers
from spacy_transformers import TransformersLanguage, TransformersWordPiecer, \
    TransformersTok2Vec  # Imports specific components from the spacy_transformers library.
import tensorflow as tf  # Imports the TensorFlow library for machine learning and deep learning.
import requests  # Imports the requests library for making HTTP requests.
from bs4 import BeautifulSoup  # Imports BeautifulSoup from the bs4 library for web scraping.
from urllib.parse import urlparse, \
    urljoin  # Imports specific functions from the urllib.parse library for working with URLs.
from transformers import AutoTokenizer, \
    RobertaModel  # Imports specific components from the transformers library for working with pre-trained models.
import nltk  # Imports the nltk library for natural language processing tasks.
import re  # Imports the re library for regular expressions.
#import sys  # Imports the sys library for system-related operations.
import tkinter as tk  # Imports the tkinter library for creating a graphical user interface (GUI).
from tkinter import filedialog  # Imports the filedialog submodule from tkinter for file selection dialogs.
from tkinter import ttk  # Imports the ttk submodule from tkinter for themed widgets.
import evtx  # Imports the Evtx module from the Evtx library for working with Windows Event Logs.
import openai  # Imports the openai library for interacting with the GPT-3 API.
#import threading  # Imports the threading library for managing threads.
#from tqdm import tqdm  # Imports tqdm for creating loading bars in the GUI.
#import subprocess  # Imports the subprocess module for running subprocesses.
import sys

print("Python Version:", sys.version)  # Prints the python version

# Add the path to the spacy_transformers library (you may not need this if the library is installed in your virtual environment)
sys.path.append("C:\\Users\\kroms\\.conda\\envs\\LLM_Test\\Lib\\site-packages\\spacy_transformers-1.2.5.dist-info")

# Initialize NLTK
nltk.download('punkt')

# Load a pre-trained RoBERTa tokenizer
tokenizer = AutoTokenizer.from_pretrained("roberta-base")
model = RobertaModel.from_pretrained('roberta-base')

# Load a Transformers pipeline with RoBERTa
nlp_transformers = TransformersLanguage(trf_name="roberta-base", meta={"lang": "en"})
word_piecer = TransformersWordPiecer.from_pretrained("roberta-base")
tok2vec = TransformersTok2Vec.from_pretrained("roberta-base")
nlp_transformers.add_pipe(word_piecer, before="ner")
nlp_transformers.add_pipe(tok2vec, before="ner")

# Check TensorFlow version
print("TensorFlow version:", tf.__version__)

# Initialize a list to store visited URLs
visited_urls = []


# Web scraping function
def scrape_web_data(url):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract text from the web page
            text = soup.get_text()

            # Add the URL to the list of visited URLs
            visited_urls.append(url)

            # Find and follow links on this page
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and href.startswith(('http://', 'https://')):
                    # Ensure that the link is an absolute URL
                    next_url = href
                else:
                    # If the link is relative, make it absolute
                    next_url = urljoin(url, href)

                # Check if we have not visited the URL already
                if next_url not in visited_urls:
                    # Recursively scrape the next URL
                    scrape_web_data(next_url)

            # Return the text after scraping
            return text

    except Exception as e:
        print("Error:", str(e))

    # Return None in the case of an error
    return None


# Function to process text using RoBERTa-based LLM
def process_with_llm(text):
    doc = nlp_transformers(text)

    # Access token-level information, excluding whitespace tokens
    for token in doc:
        if not token.is_space:
            print("Text:", token.text)
            print("Lemma:", token.lemma_)
            print("Part of Speech:", token.pos_)
            print("Tag:", token.tag_)


# Function to analyze log entries in a similar format
def analyze_log_entry(log_entry):
    # Define a regular expression pattern to extract relevant information
    pattern = r"Application '([^']+)' \(pid (\d+)\) cannot be restarted - Application SID does not match Conductor SID\."
    match = re.match(pattern, log_entry)

    if match:
        application_path = match.group(1)
        pid = match.group(2)

        # Analyze or process the extracted information as needed
        print("Application Path:", application_path)
        print("PID:", pid)
    else:
        print("Log entry does not match the expected format:", log_entry)


# Specify the starting URL
start_url = "https://answers.microsoft.com/en-us/windows/forum/all/"  # Replace with the URL of the web page you want to scrape

# Scrape and process web data
scraped_text = scrape_web_data(start_url)

# Use the scraped and processed data for training your LLM
if scraped_text:
    # Process the scraped text using the RoBERTa-based LLM
    process_with_llm(scraped_text)
else:
    print("No data returned from web scraping.")

# Analyze a sample Windows log entry (customize this for your log file)
sample_log_entry = "Application 'C:\\Program Files\\WindowsApps\\MicrosoftWindows.Client.WebExperience_423.23500.0.0_x64__cw5n1h2txyewy\\Dashboard\\Widgets.exe' (pid 12436) cannot be restarted - Application SID does not match Conductor SID.."
analyze_log_entry(sample_log_entry)

# Sets the API key
# Replace the "ENTER KEY HERE" with your OpenAI key
openai.api_key = "PLACEHOLDER"

# Sets the chat engine model to be used
model_engine = "text-davinci-003"

# Sets the log directory path
LOG_DIRECTORY = "C:\Windows\System32\winevt\Logs"  # commented until permissions error is resolved r"C:\Windows\System32\winevt\Logs"

# Load the spaCy language model
nlp = spacy.load('en_core_web_sm')

#  Defines a global variable to store log_files
global log_files
log_files = []


# Function to analyze log files
def analyze_logs(log_files, text_widget):
    # Enables the widget for writing
    text_widget.config(state='NORMAL')

    # Deletes any pre-existing content
    text_widget.delete(1.0, tk.END)

    # Iterate through each log file
    for file_path in log_files:
        # Opens the log file
        with evtx.evtx(file_path) as log:
            for record in log.records():
                log_contents = record.xml()

                # Insert the log contents into the text widget
                text_widget.insert(tk.END, log_contents)
                text_widget.insert(tk.END, "\n")

    # Disables the text widget, making it read-only
    text_widget.config(state='disabled')


# Function to process log files and interact with ChatGPT
def send_query_and_display_response(log_files, log_contents, analysis_text, progress_bar):
    #  Clear any existing content in the "Log Contents" tab
    log_contents_text.config(state='normal')
    log_contents_text.delete(1.0, tk.END)

    #  Clear any existing content in the "Analysis" tab
    analysis_text.config(state='normal')
    analysis_text.delete(1.0, tk.END)

    for file_path in log_files:
        with evtx.Evtx(file_path) as log:
            for record in log.records():
                log_contents = record.xml()

                #  Display the log contents in the "Log Contents" tab
                log_contents_text.insert(tk.END, log_contents)
                log_contents_text.insert(tk.END, "\n")
                log_contents_text.see(tk.END)

                #  Disable the "Log Contents" text widget, making it read-only
                log_contents_text.config(state='disabled')

                # Send log_contents to ChatGPT for analysis
                response = openai.Completion.create(
                    engine=model_engine,
                    prompt=log_contents,
                    max_tokens=4096
                )
                response_text = response.choices[0].text

                # Display the ChatGPT response in the "Analysis" tab
                analysis_text.insert(tk.END, f"ChatGPT: {response_text}\n")
                analysis_text.insert(tk.END, "\n")
                analysis_text.see(tk.END)

                # Update the progress bar
                progress_bar.update(1)

    #  Disable the "Analysis" text widget, making it read-only
    analysis_text.config(state='disabled')


# Function to open log files and interact with ChatGPT using threading
def open_logs_and_interact_with_chatgpt(text_widget, progress_bar):
    #  Access the global log_files variable
    global log_files

    # Remove the warning message
    text_widget.delete(1.0, tk.END)

    # Open file dialog to select log files in the log directory
    log_files = filedialog.askopenfilenames(initialdir=LOG_DIRECTORY, filetypes=[('Log Files', '*.evtx')])

    if log_files:
        total_records = 0  # Initializes the total_records count

        # Calculate the total number of log records for progress bar
        for file_path in log_files:
            with evtx.Evtx(file_path) as log:
                total_records += len(list(log.records()))

        # Configure the progress bar
        progress_bar['maximum'] = total_records
        progress_bar['value'] = 0  # Initialize progress to 0

        #  Call the send_query_and_display_response function with log_files
        send_query_and_display_response(log_files, log_contents_text, analysis_text, progress_bar)

        # Create a thread to process logs and interact with ChatGPT
        # thread = threading.Thread(target=send_query_and_display_response, args=(log_files, text_widget, progress_bar))
        # thread.start()
    else:
        text_widget.insert(tk.END, "No log files selected. \n")


# Create the main GUI interface
root = tk.Tk()
root.title("Log Analyzer")

# Create a notebook for three tabs
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# First tab: Warning message and current version
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='Warning & Version')

# Second tab: Display log contents
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Log Contents')

# Third tab: Display analysis results
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text='Analysis')

# Create a vertical scrollbar
scrollbar = tk.Scrollbar(tab2)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a text widget for displaying log contents
log_contents_text = tk.Text(tab2, height=25, width=65, yscrollcommand=scrollbar.set, state=tk.DISABLED)

# Disable widget expansion
log_contents_text.pack_propagate(False)

# Add the text widget to the frame
log_contents_text.pack(fill='both', expand=True)

# Configure the scrollbar to scroll the log contents text widget
scrollbar.config(command=log_contents_text.yview)
log_contents_text.config(yscrollcommand=scrollbar.set)

# Create a vertical scrollbar for analysis results
analysis_scrollbar = tk.Scrollbar(tab3)
analysis_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a text widget for displaying analysis results
analysis_text = tk.Text(tab3, height=25, width=65, yscrollcommand=analysis_scrollbar.set, state=tk.DISABLED)
analysis_text.pack(fill='both', expand=True)

# Configure the scrollbar to scroll the analysis text widget
analysis_scrollbar.config(command=analysis_text.yview)
analysis_text.config(yscrollcommand=analysis_scrollbar.set)

# Add the warning message and version to the first tab
warning_message = (
    "IMPORTANT WARNING:\n"
    "THIS IS AN UNFINISHED TEST BUILD\n"
    "Version: Alpha 1.5"
)
warning_label = tk.Label(tab1, text=warning_message, font=("Arial", 16, "bold"))
warning_label.pack()

# Creates a button to analyze logs and display the result in the "Analysis" tab
analyze_button = tk.Button(tab3, text="Analyze Logs with ChatGPT",
                           command=lambda: open_logs_and_interact_with_chatgpt(analysis_text, progress_bar))
analyze_button.pack()

# Creates a progress bar for log analysis in the "Analysis" tab
progress_bar = ttk.Progressbar(tab3, orient='horizontal', mode='determinate')
progress_bar.pack(fill='both', expand=True)

# Start the GUI event loop
root.mainloop()
