import os
import subprocess
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Set upload and output folders
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded file
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    return (
        jsonify({"message": "File uploaded successfully", "file_path": file_path}),
        200,
    )


@app.route("/convert", methods=["POST"])
def convert_to_gif():
    data = request.json

    video_path = data.get("file_path")
    resolution = data.get("resolution", "320:-1")  # Default resolution
    frame_rate = data.get("frame_rate", 10)  # Default frame rate
    start_time = data.get("start_time", 0)  # Default start time
    end_time = data.get("end_time", None)  # Default end time

    if not video_path or not os.path.exists(video_path):
        return jsonify({"error": "Invalid video file"}), 400

    # Set output GIF path
    file_name = os.path.basename(video_path).rsplit(".", 1)[0]
    output_path = os.path.join(app.config["OUTPUT_FOLDER"], f"{file_name}.gif")

    # Construct FFmpeg command
    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        f"scale={resolution},fps={frame_rate}",
        "-ss",
        str(start_time),
    ]

    if end_time:
        command.extend(["-to", str(end_time)])

    command.append(output_path)

    # Run FFmpeg command
    try:
        subprocess.run(
            command, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"FFmpeg error: {e.stderr.decode('utf-8')}"}), 500

    return jsonify({"message": "Conversion successful", "gif_path": output_path}), 200


if __name__ == "__main__":
    app.run(debug=True)
