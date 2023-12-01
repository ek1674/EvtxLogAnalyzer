#  This is a beta LLM for NLP, needs to be trained on a custom database THIS SECTION NEEDS TO BE UPDATED
#  Time spent on this == 50 hours

# Goals
#  Display warning message and application version in tab1 (DONE)
#  Display log content in tab2 without log analysis taking place (NEEDS TO BE DONE)
#  Analyze logs and provide an explanation using NLP that is easy to understand
#  Convert from a .py to a .exe using PyInstaller or something similar
#  Expand ability to automatically parse and classify different log types beyond the current Windows and Apache formats
#  Train machine learning models to categorize logs based on source, level, message format etc.
#  Lookup tables to map log codes/IDs to human-readable descriptions
#  Interactive charts showing trends in different log metrics over time
#  Ability to filter logs by source, date, severity level via GUI controls
#  Set notification rules based on log patterns indicating problems
#  Real-time alerts for increases in particular error rates
#  Email/SMS alerts when high priority issues detected, or some sort of alert system

import nltk  # Imports the nltk library for natural language processing tasks
import re  # Imports the re library for regular expressions.
import tkinter as tk  # Imports the tkinter library for creating a graphical user interface (GUI).
from tkinter import filedialog  # Imports the filedialog submodule from tkinter for file selection dialogs.
from tkinter import ttk  # Imports the ttk submodule from tkinter for themed widgets.
import sys  # Import the sys module for system-related operations
import \
    openai  # Imports the openai library for interacting with the GPT-3 API. (WILL BE REMOVED IN FINAL RELEASE, FOR PROTOTYPE)
import evtx as evtx  # Imports the Evtx module from the Evtx library for working with Windows Event Logs.
import requests  # Imports the requests library for making HTTP requests.
from bs4 import BeautifulSoup  # Import BeautifulSoup for HTML parsing
from urllib.parse import \
    urljoin  # Import urljoin to construct absolute URLs by combining a base URL with a relative URL
import tkinter.font as tkFont  # Import the font module from tkinter
import ctypes  # For interacting with Windows API, used for checking and requesting administrator privileges
import os  # Provides a way of interacting with the operating system

# Image path for the logo
image_path = "C:/Users/kroms/Documents/SIP405_Logo.jpg"

print("Python Version:", sys.version)  # Prints the python version
print(dir(evtx))  # Prints evtx directory

# Define NLTK specific downloads if not already downloaded
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Sets the chat engine model to be used
model_engine = "text-davinci-003"

# Sets the log directory path
LOG_DIRECTORY = "C:\Windows\System32\winevt\Logs"

# Check if the script is running with administrator privileges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Request administrator privileges if not already running as administrator
def run_as_admin():
    if not is_admin():
        #  Relaunch the script with administrator privileges using ShellExecuteW
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# Run the script as administrator
run_as_admin()

# Function to process text using NLTK-based methods
def process_with_nltk(text):
    # Tokenize the text using NLTK
    tokens = nltk.word_tokenize(text)

    # Apply part-of-speech tagging with nltk
    tagged_tokens = nltk.pos_tag(tokens)

    for token, tag in tagged_tokens:
        print("Text:", token)
        print("Part of Speech:", tag)


# List to keep track of visited URLs during web scraping
visited_urls = []


# Function to scrape web data (GOING TO BE CHANGED IN FUTURE RELEASES, PROOF OF CONCEPT FOR NOW)
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


# The starting URL for web scraping
start_url = "https://answers.microsoft.com/en-us/windows/forum/all/"

# Scrape and process web data
scraped_text = scrape_web_data(start_url)

# Use the scraped and processed data for NLTK processing
if scraped_text:
    # Process the scraped text using NLTK
    process_with_nltk(scraped_text)
else:
    print("No data returned from web scraping.")

# Analyze a sample log entry
sample_log_entry = "Application 'C:\\Program Files\\WindowsApps\\MicrosoftWindows.Client.WebExperience_423.23500.0.0_x64__cw5n1h2txyewy\\Dashboard\\Widgets.exe' (pid 12436) cannot be restarted - Application SID does not match Conductor SID.."
analyze_log_entry(sample_log_entry)

# Sets the API key
# Replace the "PLACEHOLDER" with your OpenAI API key
openai.api_key = "PLACEHOLDER"

#  Defines a global variable to store log_files
global log_files
log_files = []


# Function to analyze log files
def analyze_logs(log_files, text_widget):
    text_widget.config(state='NORMAL')
    text_widget.delete(1.0, tk.END)

    try:
        for file_path in log_files:
            with evtx.PyEvtxParser(file_path) as log:
                for record in log.records():
                    log_contents = record.xml()
                    text_widget.insert(tk.END, log_contents)
                    text_widget.insert(tk.END, "\n")
    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        text_widget.insert(tk.END, f"Error: {error_message}\n")
    finally:
        text_widget.config(state='disabled')


# Function to process log files and interact with ChatGPT and display the log contents in tab2
def send_query_and_display_response(log_files, log_contents_text, analysis_text, progress_bar, notebook):
    #  Retrieve the log_contents_text_widget from the tab2 notebook
    tab2 = notebook.nametowidget(notebook.winfo_children()[1])  # Update with the correct tab index
    log_contents_text = tab2.winfo_children()[0]

    if log_contents_text is None:
        print("Error: log_contents_text is None.")
        return
    log_contents_text.config(state='normal')
    log_contents_text.delete(1.0, tk.END)

    analysis_text.config(state='normal')
    analysis_text.delete(1.0, tk.END)

    try:
        if not log_files:
            display_log_contents_in_tab2(log_contents_text)
            log_contents_text.config(state='disabled')
            analysis_text.config(state='disabled')
            return

        for file_path in log_files:
            with evtx.PyEvtxParser(file_path) as log:
                for record in log.records():
                    log_contents = record.xml()

                    log_contents_text.insert(tk.END, log_contents)
                    log_contents_text.insert(tk.END, "\n")
                    log_contents_text.see(tk.END)

                    response = openai.Completion.create(
                        engine=model_engine,
                        prompt=log_contents,
                        max_tokens=4096
                    )
                    response_text = response.choices[0].text

                    analysis_text.insert(tk.END, f"ChatGPT: {response_text}\n")
                    analysis_text.insert(tk.END, "\n")
                    analysis_text.see(tk.END)

                    progress_bar.update(1)

        log_contents_text.config(state='disabled')
        analysis_text.config(state='disabled')

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        analysis_text.insert(tk.END, f"Error: {error_message}\n")
        analysis_text.config(state='disabled')


# Function to display log contents in tab 2
def display_log_contents_in_tab2(log_contents_text):
    log_contents_text.config(state='normal')
    log_contents_text.delete(1.0, tk.END)

    # Create a centered bold tag for the message
    centered_bold_tag = tkFont.Font(family="Arial", size=16, weight="bold")
    log_contents_text.tag_configure('center', justify='center', font=centered_bold_tag)

    # Insert the message with the centered bold format and line breaks
    log_contents_text.insert(tk.END, "No Log File Selected,\nPlease Select a File in the Analysis Tab", 'center')

    log_contents_text.config(state='disabled')


# Function to open log files and interact with ChatGPT using threading
def open_logs_and_interact_with_chatgpt(text_widget, progress_bar, log_contents_text=None):
    global log_files
    global log_contents

    # Remove the warning message
    text_widget.delete(1.0, tk.END)

    # Open file dialog to select log files in the log directory
    log_files = filedialog.askopenfilenames(initialdir=LOG_DIRECTORY, filetypes=[('Log Files', '*.evtx')])

    if log_files:
        total_records = 0  # Initializes the total_records count

        # Calculate the total number of log records for progress bar
        for file_path in log_files:
            log = evtx.PyEvtxParser(file_path)
            try:
                total_records += len(list(log.records()))
            finally:
                #  No need for log.close(), it's handled by the 'with' statement already
                pass

        # Configure the progress bar
        progress_bar['maximum'] = total_records
        progress_bar['value'] = 0  # Initialize progress to 0

        #  Call the send_query_and_display_response function with log_files
        send_query_and_display_response(log_files, log_contents_text, analysis_text, progress_bar, notebook)

        # Create a thread to process logs and interact with ChatGPT
        # thread = threading.Thread(target=send_query_and_display_response, args=(log_files, text_widget, progress_bar))
        # thread.start()
    else:
        text_widget.insert(tk.END, "No log files selected. \n")


def read_evtx_logs(file_path):
    with evtx.PyEvtxParser(file_path) as log:
        for record in log.records():
            log_contents = record.xml()
            #  Do something with log contents
            print(log_contents)


# Hook into GUI button to select log file (POSSIBLY CREATES ERROR HERE)
def select_logs():
    try:
        file_path = filedialog.askopenfilename()
        if file_path:
            read_evtx_logs(file_path)
    except PermissionError as e:
        print(f"PermissionError: {e}. Check file permissions.")
    except Exception as e:
        print(f"Error: {e}")


# Create the main GUI interface
root = tk.Tk()
root.title("LogFileAI")

# Create a notebook for three tabs
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# First tab: Warning message and current version
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='Warning & Version')

# Create a warning label
warning_message = (
    "IMPORTANT WARNING:\n"
    "THIS IS AN UNFINISHED TEST BUILD\n"
    "Version: Alpha 1.6"
)

# Create the warning label and pack it at the top
warning_label = tk.Label(tab1, text=warning_message, font=("Arial", 16, "bold"))
warning_label.pack()

# Load the application Logo
img = tk.PhotoImage(file=image_path)

# Get the height and width of the image
image_width = img.width()
image_height = img.height()

# Create a canvas inside the label and place the image in it
canvas = tk.Canvas(tab1, width=img.width(), height=img.height())
canvas.create_image(0, 0, anchor='nw', image=img)
canvas.pack(side="bottom", anchor="n", pady=(10, 125))  # Sticking to bottom right corner with padding

# Use a Tkinter PhotoImage for the label's image
tk_img = tk.PhotoImage(file=image_path)
# Set the image on the canvas
canvas.create_image(0, 0, anchor='nw', image=tk_img)
# Make sure to keep a reference to the image
canvas.image = tk_img

# Second tab: Display log contents
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Log Contents')

# Create a text widget for displaying log contents in tab2
log_contents_text = tk.Text(tab2, height=25, width=65, state=tk.DISABLED)
log_contents_text.pack(fill='both', expand=True)
log_contents_text.config(state='disabled')

# Display the message in tab2 upon application start
display_log_contents_in_tab2(log_contents_text)

# Third tab: Display analysis results
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text='Analysis')

# Create a vertical scrollbar for analysis results
analysis_scrollbar = tk.Scrollbar(tab3)
analysis_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a text widget for displaying analysis results
analysis_text = tk.Text(tab3, height=25, width=65, yscrollcommand=analysis_scrollbar.set, state=tk.DISABLED)
analysis_text.pack(fill='both', expand=True)
analysis_scrollbar.config(command=analysis_text.yview)
analysis_text.config(yscrollcommand=analysis_scrollbar.set)

# Add the button to analyze logs in the "Analysis" tab (tab3)
analyze_button = tk.Button(tab3, text="Analyze Logs with ChatGPT",
                           command=lambda: open_logs_and_interact_with_chatgpt(analysis_text, progress_bar))
analyze_button.pack()

# Create a progress bar for log analysis in the "Analysis" tab
progress_bar = ttk.Progressbar(tab3, orient='horizontal', mode='determinate')
progress_bar.pack(fill='both', expand=True)

# Start the GUI event loop
root.mainloop()
