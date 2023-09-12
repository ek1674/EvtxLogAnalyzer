# This build of my software will, hopefully, incorporate the GUI and log sorting portion of the previous dev builds.
# It is important to note that AI, nor sorting, has yet been implemented


# Imports the necessary libraries
import tkinter as tk #imports the tkinter library, used to create the GUI
from tkinter import filedialog #this is a submodule from tkinter, used for file selection
from tkinter import ttk #import for themed widgets
import Evtx.Evtx as evtx #used to read windows event logs
import spacy #imports spaCy library, a natural language processing (NLP) library
import openai #imports the openai library which is used for interacting with the GPT-3 API
import threading #provides a way to create and manage threads
from tqdm import tqdm #adds in loading bar to enhance user experience

#Sets the API key
#Replace the "ENTER KEY HERE" with your OpenAI key
openai.api_key = "PLACEHOLDER"

# Sets the chat engine model to be used
model_engine = "text-davinci-003"

# Sets the log directory path
LOG_DIRECTORY = " "  # commented until permissions error is resolved r"C:\Windows\System32\winevt\Logs"

# Load the spaCy language model
nlp = spacy.load('en_core_web_sm')


# Function to analyze log files
def analyze_logs(log_files, text_widget):
    # Enables the widget for writing
    text_widget.congif(state='NORMAL')

    # Deletes any pre-existing content
    text_widget.delete(1.0, tk.END)

    # Iterate through each log file
    for file_path in log_files:
        # Opens the log file
        with evtx.Evtx(file_path) as log:
            for record in log.records():
                log_contents = record.xml()

                # Insert the log contents into the text widget
                text_widget.insert(tk.END, log_contents)
                text_widget.insert(tk.END, "\n")

    # Disables the text widget, making it read-only
    text_widget.config(state='disabled')

# Function to process log files and interact with ChatGPT
def send_query_and_display_response(log_files, text_widget, progress_bar):
    for file_path in log_files:
        with evtx.Evtx(file_path) as log:
            for record in log.records():
                log_contents = record.xml()

                #Send log_contents to ChatGPT for analysis
                response = openai.Completion.create(
                    engine=model_engine,
                    promt=log_contents,
                    max_tokens=50
                )
                response_text = response.choices[0].text

                # Display the ChatGPT response in the GUI text widget
                text_widget.insert(tk.END, f"ChatGPT: {response_text}\n")
                text_widget.insert(tk.END, "\n")
                text_widget.see(tk.END)

                # Update the progress bar
                progess_bar.update(1)

# Function to open log files and interact with ChatGPT using threading
def open_logs_and_interact_with_chatgpt(text_widget, progress_bar):
    # Remove the warning message
    text_widget.delete(1.0, tk.END)

    # Open file dialog to select log files in the log directory
    log_files = filedialog.askopenfilenames(initialdir=LOG_DIRECTORY, filetypes=[('Log Files', '*.evtx')])

    if log_files:
        total_records = 0 # Initializes the total_records count

        #Calculate the total number of log records for progress bar
        for file_path in log_files:
            with evtx.Evtx(file_path) as log:
                total_records += len(list(log.records()))

        # Configure the progress bar
        progress_bar['maximum'] = total_records
        progress_bar['value'] = 0 # Initialize progress to 0
        # Create a thread to process logs and interact with ChatGPT
        thread = threading.Thread(target=send_query_and_display_response, args=(log_files, text_widget, progress_bar))
        thread.start()
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
    "Version: Alpha 1.4"
)
warning_label = tk.Label(tab1, text=warning_message, font=("Arial", 16, "bold"))
warning_label.pack()

# Creates a button to analyze logs and display the result in the "Analysis" tab
analyze_button = tk.Button(tab3, text="Analyze Logs with ChatGPT", command=lambda: open_logs_and_interact_with_chatgpt(analysis_text, progress_bar))
analyze_button.pack()

# Creates a progress bar for log analysis in the "Analysis" tab
progress_bar = ttk.Progressbar(tab3, orient='horizontal', mode='determinate')
progress_bar.pack(fill='both', expand=True)

# Start the GUI event loop
root.mainloop()