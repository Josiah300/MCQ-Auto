from googleapiclient.discovery import build
from google.oauth2 import service_account
from docx import Document
import json
import os
from flask import Flask, request, jsonify

# ✅ Define SCOPES at the top before using it
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly"
]

# ✅ Read service account credentials from environment variables
SERVICE_ACCOUNT_INFO = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

# ✅ Create credentials object
creds = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES
)

# ✅ Create Google Drive service instance
drive_service = build("drive", "v3", credentials=creds)

# ✅ Initialize Flask app
app = Flask(__name__)

# Function to extract text and detect bold formatting from DOCX
def extract_mcqs_from_docx(file_path):
    doc = Document(file_path)  # ✅ Corrected the file path
    mcqs = []
    current_question = None
    current_options = []
    correct_answer = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        for run in para.runs:
            if run.bold:  # Detect bold text (correct answer)
                correct_answer = run.text.strip()

        if not current_question:
            current_question = text  # First line is the question
        else:
            current_options.append(text)  # Next lines are options

        if len(current_options) == 4:  # Ensure we collect exactly 4 options
            mcqs.append({
                "question": current_question,
                "options": current_options,
                "correct_answer": correct_answer
            })
            current_question = None
            current_options = []
            correct_answer = None

    return mcqs


# Function to download DOCX file from Google Drive
def download_file(file_id, file_path):
    request = drive_service.files().get_media(fileId=file_id)
    with open(file_path, "wb") as f:
        f.write(request.execute())


# Replace with the actual file ID from Google Drive
file_id = "1DRz09GPJlUffDidOaWzXTlMdNiqig7Uq"
file_path = "downloaded.docx"

# Download the file from Google Drive
download_file(file_id, file_path)

# Extract MCQs from the DOCX file
mcqs = extract_mcqs_from_docx(file_path)

# Print the extracted questions and correct answers
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


@app.route('/extract_mcqs', methods=['POST'])
def extract_mcqs():
    data = request.json
    file_id = data.get("file_id")

    if not file_id:
        return jsonify({"error": "No file_id provided"}), 400

    # Download and process the DOCX file
    file_path = "downloaded.docx"
    download_file(file_id, file_path)
    mcqs = extract_mcqs_from_docx(file_path)

    return jsonify({"mcqs": mcqs})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
