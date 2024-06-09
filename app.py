import os
from flask import Flask, request, render_template, send_from_directory, jsonify
import cv2
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Create the uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Load color data from a CSV file into a Pandas DataFrame
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv("colors.csv", names=index)

def get_color_name(R, G, B):
    min_distance = 1000
    cname = ""
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= min_distance:
            min_distance = d
            cname = csv.loc[i, "color_name"]
    return cname

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return render_template('index.html', filename=file.filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/color', methods=['POST'])
def get_color():
    try:
        x = int(request.form['x'])
        y = int(request.form['y'])
        filename = request.form['filename']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        img = cv2.imread(filepath)
        b, g, r = img[y, x]
        # Convert numpy.uint8 to Python int
        b = int(b)
        g = int(g)
        r = int(r)
        color_name = get_color_name(r, g, b)
        print(f"Coordinates: ({x}, {y}) - Color: {color_name} (R: {r}, G: {g}, B: {b})")  # Debug output
        return jsonify({'color_name': color_name, 'r': r, 'g': g, 'b': b})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
