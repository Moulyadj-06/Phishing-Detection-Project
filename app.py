import os
import json
import pandas as pd
import joblib
from urllib.parse import urlparse
from flask import Flask, render_template, request

app = Flask(__name__)

# Upload settings
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv", "xlsx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load trained phishing detection model
model = joblib.load('model/phishing_model.joblib')

# File to store statistics
STATS_FILE = "stats1.json"


# Function to check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Function to extract URL features
def extract_features(url):
    parsed_url = urlparse(url)
    return [
        len(url),
        url.count('.'),
        url.count('/'),
        url.count('?'),
        url.count('='),
        url.count('@'),
        url.count('-'),
        1 if parsed_url.scheme == "https" else 0
    ]


# Function to update stats.json dynamically
def update_stats(url, result):
    if not os.path.exists(STATS_FILE):
        stats = {"total_urls": 0, "phishing_urls": 0, "legit_urls": 0, "urls": []}
    else:
        with open(STATS_FILE, "r") as f:
            try:
                stats = json.load(f)
            except json.JSONDecodeError:
                stats = {"total_urls": 0, "phishing_urls": 0, "legit_urls": 0, "urls": []}

    stats["total_urls"] += 1
    if result == "Phishing":
        stats["phishing_urls"] += 1
    else:
        stats["legit_urls"] += 1

    stats["urls"].append({"url": url, "result": result})

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)


# Home Route
@app.route('/')
def home():
    return render_template('dashboard.html')


# Phishing URL Prediction Route
@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        url = request.form['url']
        features = extract_features(url)
        probability = model.predict_proba([features])[0][1]
        threshold = 0.8  # Adjust as needed
        result = "Phishing" if probability > threshold else "Legitimate"
        update_stats(url, result)
        return render_template('result.html', url=url, result=result, probability=probability)
    return render_template('index.html')


# Statistics Route
@app.route('/stats')
def stats():
    if not os.path.exists(STATS_FILE):
        stats = {"total_urls": 0, "phishing_urls": 0, "legit_urls": 0, "urls": []}
    else:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    phishing_rate = (stats["phishing_urls"] / stats["total_urls"] * 100) if stats["total_urls"] > 0 else 0
    return render_template('stats.html', stats=stats, phishing_rate=phishing_rate)


# Dataset Viewer Route
@app.route('/dataset', methods=['GET', 'POST'])
def dataset():
    if request.method == "POST":
        if "dataset" not in request.files:
            return "No file part"

        file = request.files["dataset"]

        if file.filename == "":
            return "No selected file"

        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            if file.filename.endswith(".csv"):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)

            tables = df.to_html(classes="table table-striped", index=False)
            return render_template("dataset.html", tables=tables)

    return render_template("dataset.html")


if __name__ == '__main__':
    app.run(debug=True)
