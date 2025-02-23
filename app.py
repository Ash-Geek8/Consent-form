from flask import Flask, render_template, request, redirect, url_for
import json
import csv
import os
import requests
import base64
from datetime import datetime, date

app = Flask(__name__)
JSON_FILE = "participants.json"
CSV_FILE = "participants.csv"
PORT = int(os.environ.get("PORT", 5000))
GITHUB_REPO = os.environ.get("https://github.com/Ash-Geek8/Consent-form/")  # GitHub repository URL
GITHUB_TOKEN = os.environ.get("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")  # GitHub token for authentication

def load_data():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)
    upload_to_github(JSON_FILE)

def save_to_csv():
    data = load_data()
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Full Name", "Email", "Phone Number", "Date"])
        for entry in data:
            formatted_date = datetime.strptime(entry["consent_date"], "%Y-%m-%d").strftime("%d-%m-%Y")
            writer.writerow([entry["full_name"], entry["email"], entry["phone_number"], formatted_date])
    upload_to_github(CSV_FILE)

def upload_to_github(filename):
    if not GITHUB_REPO or not GITHUB_TOKEN:
        print("GitHub repository or token not set.")
        return
    
    with open(filename, "rb") as file:
        content = base64.b64encode(file.read()).decode("utf-8")
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha", "") if response.status_code == 200 else ""
    
    data = {
        "message": f"Update {filename}",
        "content": content
    }
    
    if sha:
        data["sha"] = sha  # Include SHA only when updating an existing file
    
    put_response = requests.put(url, headers=headers, json=data)
    if put_response.status_code in [200, 201]:
        print(f"Successfully uploaded {filename} to GitHub.")
    else:
        print(f"Failed to upload {filename}. Response: {put_response.text}")

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
