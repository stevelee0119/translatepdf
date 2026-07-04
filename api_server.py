#!/usr/bin/env python3
"""
Flask-based API server for PDF translation
Supports both local deployment and cloud hosting (Render, Railway, etc.)
"""

import os
import re
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Tuple

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import requests
from pdf2zh.doclayout import OnnxModel
from pdf2zh.high_level import translate


# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
STATIC_DIR = SCRIPT_DIR / "docs"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")
CORS(app)  # Enable CORS for GitHub Pages

# Configuration
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / "translatepdf"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf"}

# Store for task results
tasks = {}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def download_google_drive(url: str) -> Path:
    """Download file from Google Drive shared link"""
    if not url:
        raise ValueError("Google Drive 링크가 비어 있습니다.")

    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        match = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError("유효한 Google Drive 공유 링크를 입력하세요.")

    file_id = match.group(1)
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    session = requests.Session()
    response = session.get(download_url, stream=True, timeout=30)
    token = None
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            token = value
            break

    if token:
        download_url = f"https://drive.google.com/uc?export=download&confirm={token}&id={file_id}"
        response = session.get(download_url, stream=True, timeout=30)

    target_path = UPLOAD_FOLDER / f"google_drive_{file_id}.pdf"

    with open(target_path, "wb") as fd:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                fd.write(chunk)

    return target_path


@app.route("/")
def index():
    """Serve index.html"""
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    if path.startswith("api/") or path in ("health", "download"):
        return jsonify({"error": "엔드포인트를 찾을 수 없습니다."}), 404
    file_path = STATIC_DIR / path
    if file_path.exists() and file_path.is_file():
        return send_from_directory(STATIC_DIR, path)
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


@app.route("/api/translate", methods=["POST"])
def translate_pdf():
    """
    Translate PDF file
    
    Expected form data:
    - file: PDF file (optional if gdrive_url is provided)
    - gdrive_url: Google Drive link (optional if file is provided)
    - service: Translation service (default: google)
    - lang_in: Input language code (default: en)
    - lang_out: Output language code (default: ko)
    - threads: Number of translation threads (default: 4)
    """
    try:
        # Validate input
        file = request.files.get("file")
        gdrive_url = request.form.get("gdrive_url", "").strip()

        if not file and not gdrive_url:
            return jsonify({"error": "파일을 업로드하거나 Google Drive 링크를 입력하세요."}), 400

        # Get parameters
        service = request.form.get("service", "google")
        lang_in = request.form.get("lang_in", "en")
        lang_out = request.form.get("lang_out", "ko")
        threads = int(request.form.get("threads", 4))

        # Get input file
        if file and file.filename != "":
            if not allowed_file(file.filename):
                return jsonify({"error": "PDF 파일만 업로드 가능합니다."}), 400
            input_pdf = UPLOAD_FOLDER / file.filename
            file.save(input_pdf)
        elif gdrive_url:
            input_pdf = download_google_drive(gdrive_url)
        else:
            return jsonify({"error": "파일 또는 링크를 입력하세요."}), 400

        # Check file size (max 100MB)
        if input_pdf.stat().st_size > 100 * 1024 * 1024:
            return jsonify({"error": "파일 크기는 100MB 이하여야 합니다."}), 400

        # Create task ID
        task_id = str(uuid.uuid4())
        output_dir = UPLOAD_FOLDER / task_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load model
        model = OnnxModel.load_onnx()

        # Translate
        result_files = translate(
            [str(input_pdf)],
            output=str(output_dir),
            lang_in=lang_in,
            lang_out=lang_out,
            service=service,
            thread=threads,
            model=model,
            callback=None,
        )

        translated_pdf = Path(result_files[0][0])

        # Store task result
        tasks[task_id] = {
            "pdf_path": str(translated_pdf),
            "filename": translated_pdf.name,
            "status": "completed",
        }

        return jsonify({
            "task_id": task_id,
            "filename": translated_pdf.name,
            "status": "completed",
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Translation error: {e}")
        return jsonify({"error": f"번역 중 오류가 발생했습니다: {str(e)}"}), 500


@app.route("/download/<task_id>", methods=["GET"])
def download_file(task_id):
    """Download translated PDF"""
    if task_id not in tasks:
        return jsonify({"error": "파일을 찾을 수 없습니다."}), 404

    task = tasks[task_id]
    pdf_path = Path(task["pdf_path"])

    if not pdf_path.exists():
        return jsonify({"error": "파일을 찾을 수 없습니다."}), 404

    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=task["filename"],
    )


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "엔드포인트를 찾을 수 없습니다."}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "서버 오류가 발생했습니다."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_ENV") == "development"

    app.run(host=host, port=port, debug=debug)
