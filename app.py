from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import json
import csv
import os
from datetime import datetime, date

app = Flask(__name__)

# File Paths
JSON_FILE = "participants.json"
CSV_FILE = "participants.csv"
PORT = 5000  # Fixed port (Render uses environment variables)

# Ensure files exist
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w") as f:
        pass  # Creates an empty file

# Load JSON Data
def load_data():
    try:
        with open(JSON_FILE, "r") as file:
            content = file.read().strip()
            return json.loads(content) if content else []
    except json.JSONDecodeError:
        return []

# Save JSON Data
def save_data(data):
    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)
    save_to_csv()

# Save to CSV
def save_to_csv():
    data = load_data()
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Full Name", "Email", "Phone Number", "Date"])
        for entry in data:
            formatted_date = datetime.strptime(entry["consent_date"], "%Y-%m-%d").strftime("%d-%m-%Y")
            writer.writerow([entry["full_name"], entry["email"], entry["phone_number"], formatted_date])

# Home Page - Consent Form
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
            return redirect(url_for("thankyou"))

    return render_template("index.html")

# Thank You Page
@app.route("/thankyou")
def thankyou():
    return render_template("thanks.html")

# File Download Route
@app.route("/download/<filename>")
def download_file(filename):
    if filename in [JSON_FILE, CSV_FILE] and os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
