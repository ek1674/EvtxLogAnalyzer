# This build of my software will, hopefully, incorporate the GUI and log sorting portion of the previous dev builds.
# It is important to note that AI, nor sorting, has yet been implemented

import openai

#Sets the API key
openai.api_key = "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"

# Sets the chat engine model to be used
model_engine = "text-davinci-003"

# Imports the necessary libraries
import tkinter as tk
from tkinter import filedialog
import Evtx.Evtx as evtx
import spacy
import os
import ctypes
import sys

# Sets the log directory path
LOG_DIRECTORY = " "  # commented until permissions error is resolved r"C:\Windows\System32\winevt\Logs"

# Load the spaCy language model
nlp = spacy.load('en_core_web_sm')


# Function to analyze log files
def analyze_logs(log_files, text_widget):
    # Clear the text widget before adding new content
    text_widget.delete(1.0, tk.END)

    for file_path in log_files:
        with evtx.Evtx(file_path) as log:
            for record in log.records():
                log_contents = record.xml()

                # Perform NLP analysis using spaCy
                doc = nlp(log_contents)

                # Extract entities from the analyzed text
                entities = [ent.text for ent in doc.ents]

                # Display entities in the GUI text widget
                text_widget.insert(tk.END, f"Entities found: {entities}\n")
                text_widget.insert(tk.END, "\n")
                text_widget.see(tk.END)


# Function to open log files
def open_logs(text_widget):
    # Inserts the warning message
    text_widget.insert(tk.END, "IMPORTANT WARNING:\n", "bold")
    text_widget.insert(tk.END, "THIS IS AN UNFINISHED TEST BUILD\n", "bold")
    text_widget.insert(tk.END, "\n", "bold")

    # Prompt for administrator credentials
    #   if os.name == "nt":
    #       # Re-run the script with elevated privileges
    #       if ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1) <= 32:
    #           return

    # Open file dialog to select log files in the log directory
    log_files = filedialog.askopenfilenames(initialdir=LOG_DIRECTORY, filetypes=[('Log Files', '*.evtx')])

    if log_files:
        # Analyze the selected log files and display entities in the GUI text widget
        analyze_logs(log_files, output_text)
    else:
        text_widget.insert(tk.END, "No log files selected. \n")


# Create the main GUI interface
root = tk.Tk()
root.title("Log Analyzer")

# Create a vertical scrollbar
scrollbar = tk.Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a text widget for displaying the output
output_text = tk.Text(root, height=25, width=65, yscrollcommand=scrollbar.set)
output_text.pack()

# Configure the scrollbar to scroll the text widget
scrollbar.config(command=output_text.yview)
output_text.config(yscrollcommand=scrollbar.set)

# Configures bold formatting for warning message, this plus the warning message can be removed at a later time
output_text.tag_configure("bold", font=("Arial", 16, "bold"))

# Create a button to open log files
button = tk.Button(root, text="Open Log Files", command=lambda: open_logs(output_text))
button.pack()

# Start the GUI event loop
root.mainloop()