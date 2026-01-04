from flask import Flask, render_template, request
from datetime import datetime
from flask import redirect

app = Flask(__name__)

# Store prediction history (temporary memory)
prediction_history = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/clear_history', methods=['POST'])
def clear_history():
    prediction_history.clear()
    return redirect('/')

@app.route('/predict', methods=['POST'])
def predict():
    inputs = {
        "age": int(request.form['age']),
        "gender": request.form['gender'],
        "tot_bilirubin": float(request.form['tot_bilirubin']),
        "direct_bilirubin": float(request.form['direct_bilirubin']),
        "tot_proteins": float(request.form['tot_proteins']),
        "albumin": float(request.form['albumin']),
        "ag_ratio": float(request.form['ag_ratio']),
        "sgpt": float(request.form['sgpt']),
        "sgot": float(request.form['sgot']),
        "alkphos": float(request.form['alkphos'])
    }

    normal_ranges = {
        "tot_bilirubin": (0.3, 1.2),
        "direct_bilirubin": (0.1, 0.4),
        "tot_proteins": (6.0, 8.3),
        "albumin": (3.5, 5.0),
        "ag_ratio": (1.0, 2.5),
        "sgpt": (7, 56),
        "sgot": (5, 40),
        "alkphos": (44, 147)
    }
    

    abnormal = []

    for key, value in inputs.items():
        if key in normal_ranges:
            low, high = normal_ranges[key]
            if value < low:
                abnormal.append(f"{key} is LOW")
            elif value > high:
                abnormal.append(f"{key} is HIGH")

    if len(abnormal) == 0:
        final_result = "✅ Normal – No Liver Disease Risk"
        status = "Normal"
    else:
        final_result = "⚠️ Liver Disease Risk Detected"
        status = "Risk"

    # Save to history
    prediction_history.append({
        "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "age": inputs["age"],
        "gender": inputs["gender"],
        "result": status
    })

    return render_template(
        'result.html',
        result=final_result,
        status=status,
        abnormal=abnormal,
        values=inputs,
        normal=normal_ranges,
        history=prediction_history
    )

if __name__ == "__main__":
    app.run(debug=True)
