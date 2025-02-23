from flask import Flask, render_template, request, redirect, url_for
import json
import csv
import os
from datetime import datetime, date
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

app = Flask(__name__)
JSON_FILE = "participants.json"
CSV_FILE = "participants.csv"
PORT = 5000  # Default Flask port

# Authenticate Google Drive
gauth = GoogleAuth()
gauth.CommandLineAuth()  # Opens a browser for authentication
drive = GoogleDrive(gauth)

def load_data():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as file:
            content = file.read().strip()  # Read and remove whitespace
            return json.loads(content) if content else []  # Load JSON if not empty
    return []

def save_data(data):
    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)
    upload_to_drive(JSON_FILE)

def save_to_csv():
    data = load_data()
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Full Name", "Email", "Phone Number", "Date"])
        for entry in data:
            formatted_date = datetime.strptime(entry["consent_date"], "%Y-%m-%d").strftime("%d-%m-%Y")
            writer.writerow([entry["full_name"], entry["email"], entry["phone_number"], formatted_date])
    upload_to_drive(CSV_FILE)

def upload_to_drive(filename):
    """Upload the given file to Google Drive"""
    try:
        file_drive = drive.CreateFile({'title': filename})
        file_drive.SetContentFile(filename)
        file_drive.Upload()
        print(f"Successfully uploaded {filename} to Google Drive.")
    except Exception as e:
        print(f"Failed to upload {filename}. Error: {e}")

@app.route("/", methods=["GET", "POST"])
def consent_form():
    if request.method == "POST":
        full_name = request.form.get("name")
        email = request.form.get("email")
        phone_number = request.form.get("phone")
        consent_date = str(date.today())
        agreement = request.form.get("agreement")
        
        if agreement:
            data = load_data()
            data.append({
                "full_name": full_name,
                "email": email,
                "phone_number": phone_number,
                "consent_date": consent_date
            })
            save_data(data)
            save_to_csv()
            return redirect(url_for("thankyou"))
        
    return render_template("index.html")

@app.route("/thankyou")
def thankyou():
    return render_template("thanks.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
