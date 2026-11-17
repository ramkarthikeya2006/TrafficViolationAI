
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pathlib import Path
from uuid import uuid4
from detector import detect_vehicles

app = Flask(__name__)
app.secret_key = "local-development-key"

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv"}

app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_video():
    if request.method == "GET":
        return render_template("upload.html")

    video = request.files.get("video")

    if not video or not video.filename:
        flash("Please select a video.")
        return redirect(url_for("upload_video"))

    filename = secure_filename(video.filename)

    if "." not in filename:
        flash("Invalid filename.")
        return redirect(url_for("upload_video"))

    extension = filename.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        flash("Upload MP4, AVI, MOV, or MKV only.")
        return redirect(url_for("upload_video"))

    saved_name = f"{uuid4().hex}.{extension}"
    saved_path = UPLOAD_DIR / saved_name

    try:
        video.save(saved_path)

        detections = detect_vehicles(saved_path)
        vehicle_count = len(detections)

        flash(
            f"AI processing complete! "
            f"Vehicle detections: {vehicle_count}"
        )

    except Exception:
        app.logger.exception("Video upload or detection failed")
        flash(
            "Video uploaded, but AI processing failed. "
            "Please check the VS Code terminal."
        )

    return redirect(url_for("upload_video"))


@app.errorhandler(413)
def file_too_large(error):
    flash("Video is too large. Maximum upload size is 200 MB.")
    return redirect(url_for("upload_video"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
