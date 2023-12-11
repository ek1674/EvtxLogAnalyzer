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

#  Imports the necessary libraries
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import sys
import openai
import Evtx as evtx  # Installed with pip install python-evtx
#from Evtx import PyEvtx
from tkinter import font as tkFont
import ctypes

#  Sets path to image file, will eventually get changed to being part of the project files
image_path = "C:/Users/kroms/Desktop/SIP405_Logo.jpg"

#  Sets the OpenAI GTP-3 model engine
model_engine = "text=davinci-003"

#  Sets the directory containing the log files
LOG_DIRECTORY = "C:/Windows/System32/winevt/logs"

#  Function to check if the script is running with admin privileges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


#  Function to get the script to run with admin privileges
def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()


#  Runs the script as admin
run_as_admin()

#  Function to analyze a log entry and extract information
def analyze_log_entry(log_entry):
    pattern = r"Application '([^`]+)' \(pid (\d+)\) cannot be restarted - Application SID does not match Conductor " \
              r"SID\."
    match = re.match(pattern, log_entry)

    if match:
        application_path = match.group(1)
        pid = match.group(2)

        print("Application Path:", application_path)
        print("PID:", pid)
    else:
        print("Log entry does not match the expected format:", log_entry)


#  Sample log entry for testing the analyze_log_entry function
sample_log_entry = "Application 'C:\\Program Files\\WindowsApps\\MicrosoftWindows.Client.WebExperience_423.23500.0" \
                   ".0_x64__cw5n1h2txeywy\\Dashboard\\Widgets.exe' (pid 12436) cannot be restarted - Application SID " \
                   "does not match Conductor SID. ."
analyze_log_entry(sample_log_entry)

# Sets the OpenAI GPT-3 API key, in full release will be replaced with PLACEHOLDER
openai.api_key = "PLACEHOLDER"

# Sets global variable to store log files
global log_files
log_files = []


#  Function to analyze logs and display them in a text widget
def analyze_logs(log_files, text_widget):
    text_widget.config(state='NORMAL')
    text_widget.delete(1.0, tk.END)

    try:
        for file_path in log_files:
            try:
                with evtx.PyEvtxParser(file_path) as log:
                #with PyEvtx.File(file_path) as log:
                #with PyEvtx.File(file_path) as log:

                    for record in log.records():
                        log_contents = record.xml()
                        text_widget.insert(tk.END, log_contents)
                        text_widget.insert(tk.END, "\n")
            except Exception as log_error:
                error_message = f"Error occurred while processing log file {file_path}: {str(log_error)}"
                print(error_message)
                text_widget.insert(tk.END, f"Error: {error_message}\n")
    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        print(error_message)
        text_widget.insert(tk.END, f"Error: {error_message}\n")
        import traceback
        traceback.print_exc()
    finally:
        text_widget.config(state='disabled')


#  Function to send queries to ChatGPT for log analysis and display the responses
def send_query_and_display_response(log_files, log_contents_text, analysis_text, progress_bar, notebook):
    tab2 = notebook.nametowidget(notebook.winfo_children()[1])
    log_contents_text = tab2.log_contents_text

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
            #with PyEvtx.File(file_path) as log:

                for record in log.records():
                    log_contents = record.xml

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


# Function to display a message when no log file is selected, working on getting it to remove message and display a
# log file
def display_log_contents_in_tab2(log_contents_text):
    log_contents_text.config(state='normal')
    log_contents_text.delete(1.0, tk.END)

    centered_bold_tag = tkFont.Font(family='Arial', size=16, weight="bold")
    log_contents_text.tag_configure('center', justify='center', font=centered_bold_tag)

    log_contents_text.insert(tk.END, "No Log File Selected,\nPlease Select a File in the Analysis Tab", 'center')

    log_contents_text.config(state='disabled')


#  Function that opens log files and interacts with ChatGPT
def open_logs_and_interact_with_chatgpt(text_widget, progress_bar, log_contents_text=None):
    global log_files

    text_widget.delete(1.0, tk.END)

    log_files = filedialog.askopenfilename(initialdir=LOG_DIRECTORY, filetypes=[('Log Files', '*evtx')])
    print("Selected Log Files:", log_files)

    if log_files:
        total_records = 0

        try:
            for file_path in log_files:
                print("Processing Log File:", file_path)

                log = evtx.PyEvtxParser(file_path)
                try:
                    total_records += len(list(log.records()))
                except Exception as parse_error:
                    print(f"Error Parsing {file_path}: {parse_error}")
                finally:
                    log.close()

        except Exception as e:
            print(f"Error occurred: {e}")
            import traceback
            traceback.print_exc()

        progress_bar['maximum'] = total_records
        progress_bar['value'] = 0

        send_query_and_display_response(log_files, log_contents_text, analysis_text, progress_bar, notebook)

    else:
        text_widget.insert(tk.END, "No log files selected/ \n")


#  Function to read and display evtx logs
def read_evtx_logs(file_path):
    try:
        with evtx.PyEvtxParser(file_path) as log:
        #with PyEvtx.File(file_path) as log:
            for record in log.records():
                log_contents = record.xml()
                print(log_contents)
    except Exception as e:
        print(f" Error occurred while processing log file {file_path}: {str(e)}")


#  Function to select logs using file dialog
def select_logs():
    try:
        file_path = filedialog.askopenfilename()
        if file_path:
            read_evtx_logs(file_path)
    except PermissionError as e:
        print(f"PermissionError: {e}. Check file permissions.")
    except Exception as e:
        print(f"Error: {e}")


#  Initializes main Tkinter window
root = tk.Tk()
root.title("LogFileAI")

#  Creates notebook with tabs
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

#  Creates and names the first tab
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='Warning & Version')

#  Creates the warning message for tab 1
warning_message = (
    "IMPORTANT WARNING:\n"
    "THIS IS AN UNFINISHED TEST BUILD\n"
    "Version: Alpha 1.6\n"
    "Errors Are Likely and Expected"
)

warning_label = tk.Label(tab1, text=warning_message, font=("Arial", 16, "bold"))
warning_label.pack()

#  Displays the image from the beginning of the code
img = tk.PhotoImage(file=image_path)

image_width = img.width()
image_height = img.height()

canvas = tk.Canvas(tab1, width=img.width(), height=img.height())
canvas.create_image(0, 0, anchor='nw', image=img)
canvas.pack(side="bottom", anchor="n", pady=(10, 125))

#  Creates and names the second tab
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Log Contents')

#  Creates a text widget to display log contents
log_contents_text = tk.Text(tab2, height=25, width=65, state=tk.DISABLED)
log_contents_text.pack(fill='both', expand=True)
log_contents_text.config(state='disabled')

#  Displays a message in case no lof file is selected
display_log_contents_in_tab2(log_contents_text)

#  Creates and names the third tab
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text='Analysis')

#  Creates a scrollbar for the analysis tab text widget
analysis_scrollbar = tk.Scrollbar(tab3)
analysis_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

#  Creates a text widget for the analysis tab
analysis_text = tk.Text(tab3, height=25, width=65, yscrollcommand=analysis_scrollbar.set, state=tk.DISABLED)
analysis_text.pack(fill='both', expand=True)
analysis_scrollbar.config(command=analysis_text.yview)
analysis_text.config(yscrollcommand=analysis_scrollbar.set)

#  Creates button to analyze logs
analyze_button = tk.Button(tab3, text="Analyze logs with ChatGPT",
                           command=lambda: open_logs_and_interact_with_chatgpt(analysis_text, progress_bar))
analyze_button.pack()

#  Creates a progress bar for analysis progress (NEEDS FURTHER REFINEMENT)
progress_bar = ttk.Progressbar(tab3, orient='horizontal', mode='determinate')
progress_bar.pack(fill='both', expand=True)

#  Starts the Tkinter mainloop
root.mainloop()
