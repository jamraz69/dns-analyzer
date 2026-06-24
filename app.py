
import streamlit as st
import cv2
import numpy as np
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def analyze_image(image_path, coordinates, radius=40):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    raw_means = {}

    for name, (x, y) in coordinates.items():
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.circle(mask, (int(x), int(y)), radius, 255, -1)
        raw_means[name] = round(cv2.mean(gray, mask=mask)[0], 3)

    active_reference = raw_means["37C_Sample"]
    blank_background = 220.0
    net_color_0 = blank_background - active_reference

    results = []
    for sample in ["4C_Sample", "25C_Sample", "37C_Sample"]:
        net_color_t = blank_background - raw_means[sample]
        remaining_activity = (net_color_t / net_color_0) * 100
        degradation = 100 - remaining_activity

        results.append({
            "Sample ID": sample,
            "Raw Mean Gray Value": raw_means[sample],
            "Net Color Index": round(net_color_t, 3),
            "Remaining Activity (%)": round(remaining_activity, 2),
            "Total Degradation (%)": round(max(0, degradation), 2)
        })

    return pd.DataFrame(results).to_dict(orient="records")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["image"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    coordinates = {
        "Blank": (float(request.form["blank_x"]), float(request.form["blank_y"])),
        "4C_Sample": (float(request.form["c4_x"]), float(request.form["c4_y"])),
        "25C_Sample": (float(request.form["c25_x"]), float(request.form["c25_y"])),
        "37C_Sample": (float(request.form["c37_x"]), float(request.form["c37_y"]))
    }

    results = analyze_image(path, coordinates)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
