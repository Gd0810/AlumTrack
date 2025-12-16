from flask import Flask, render_template, request, jsonify
import csv
import os
import base64
from datetime import datetime

app = Flask(__name__)

ALUMNI_CSV = "data/alumni.csv"
CHECKED_IN_CSV = "data/checked_in.csv"
PHOTO_DIR = "static/photos"

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)


def find_by_phone(phone):
    with open(ALUMNI_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Phone Number"].strip() == phone.strip():
                return row
    return None


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        phone = request.form.get("phone")
        user = find_by_phone(phone)

        if not user:
            return render_template("result.html", not_found=True)

        return render_template("result.html", user=user)

    return render_template("index.html")


@app.route("/checkin", methods=["POST"])
def checkin():
    data = request.json
    phone = data["phone"]
    image_data = data["image"]

    user = find_by_phone(phone)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Save image
    img_bytes = base64.b64decode(image_data.split(",")[1])
    filename = f"{phone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    img_path = os.path.join(PHOTO_DIR, filename)

    with open(img_path, "wb") as f:
        f.write(img_bytes)

    # Write to new CSV
    file_exists = os.path.isfile(CHECKED_IN_CSV)
    with open(CHECKED_IN_CSV, "a", newline="", encoding="utf-8") as f:
        fieldnames = list(user.keys()) + ["Check-in Time", "Photo"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        user["Check-in Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user["Photo"] = img_path
        writer.writerow(user)

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run( debug=True)

