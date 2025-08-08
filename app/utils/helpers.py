# utils/helpers.py

import csv
import os
from datetime import datetime

# Define the path where the logs will be saved
LOG_FILE = "data/study_logs.csv"

def log_study_entry(subject, topic, hours, productivity, mood, date):
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Format the date
    formatted_date = date.strftime('%Y-%m-%d')

    # Prepare the log entry
    entry = {
        "Date": formatted_date,
        "Subject": subject,
        "Topic": topic,
        "Hours": hours,
        "Productivity": productivity,
        "Mood": mood,
        "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Check if file exists to write header if not
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)
