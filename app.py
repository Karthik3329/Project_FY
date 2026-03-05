from flask import Flask, render_template, request, redirect, session
from datetime import datetime
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "secret123"

bcrypt = Bcrypt(app)

# ---------------- MONGODB CONNECTION ----------------
client = MongoClient("mongodb+srv://Karthik3329:Karthik_3329@cluster0.hdyb1gg.mongodb.net/")
db = client["liver_app"]

users = db["users"]
predictions = db["predictions"]

# ---------------- HOME ----------------
@app.route('/')
def home():

    if "user_id" not in session:
        return redirect("/login")

    user = users.find_one({"_id": ObjectId(session["user_id"])})

    recent_history = predictions.find(
        {"user_id": ObjectId(session["user_id"])}
    ).sort("_id", -1).limit(5)

    return render_template(
        "index.html",
        username=user["name"],
        history=list(recent_history)
    )


# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form.get("role")

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        users.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password,
            "role": role
        })

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        user = users.find_one({"email": email, "role": role})

        if user and bcrypt.check_password_hash(user["password"], password):

            session["user_id"] = str(user["_id"])
            session["role"] = user["role"]

            if role == "admin":
                return redirect("/admin")

            return redirect("/")

        return "Invalid Login"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():

    session.clear()
    return redirect("/login")


# ---------------- ADMIN PANEL ----------------
@app.route("/admin")
def admin():

    if session.get("role") != "admin":
        return redirect("/login")

    all_users = list(users.find())
    all_predictions = list(predictions.find())

    normal_count = predictions.count_documents({"result": "Normal"})
    risk_count = predictions.count_documents({"result": "Risk"})

    return render_template(
        "admin.html",
        users=all_users,
        predictions=all_predictions,
        normal_count=normal_count,
        risk_count=risk_count
    )


# ---------------- DELETE USER (ADMIN) ----------------
@app.route("/delete_user/<id>")
def delete_user(id):

    if session.get("role") != "admin":
        return redirect("/login")

    users.delete_one({"_id": ObjectId(id)})
    return redirect("/admin")


# ---------------- DELETE PREDICTION (ADMIN) ----------------
@app.route("/delete_prediction/<id>")
def delete_prediction(id):

    if session.get("role") != "admin":
        return redirect("/login")

    predictions.delete_one({"_id": ObjectId(id)})
    return redirect("/admin")


# ---------------- PREDICT ----------------
@app.route('/predict', methods=['POST'])
def predict():

    if "user_id" not in session:
        return redirect("/login")

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

        final_result = "Normal"
        status = "Normal"

    else:

        final_result = "Risk"
        status = "Risk"

    current_time = datetime.now().strftime("%d-%m-%Y %H:%M")

    predictions.insert_one({

        "user_id": ObjectId(session["user_id"]),
        "time": current_time,
        "inputs": inputs,
        "abnormal": abnormal,
        "result": status

    })

    return render_template(
        'result.html',
        result=final_result,
        status=status,
        abnormal=abnormal,
        values=inputs,
        normal=normal_ranges,
        report_time=current_time
    )


# ---------------- HISTORY ----------------
@app.route('/history')
def history():

    if "user_id" not in session:
        return redirect("/login")

    user_history = predictions.find(
        {"user_id": ObjectId(session["user_id"])}
    ).sort("_id", -1)

    return render_template(
        "history.html",
        history=list(user_history)
    )


# ---------------- VIEW REPORT ----------------
@app.route('/report/<id>')
def report(id):

    if "user_id" not in session:
        return redirect("/login")

    report = predictions.find_one({

        "_id": ObjectId(id),
        "user_id": ObjectId(session["user_id"])

    })

    if not report:
        return "Report Not Found"

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

    return render_template(
        "result.html",
        values=report["inputs"],
        abnormal=report["abnormal"],
        status=report["result"],
        normal=normal_ranges,
        report_time=report["time"]
    )


# ---------------- DELETE REPORT ----------------
@app.route("/delete/<id>")
def delete_report(id):

    if "user_id" not in session:
        return redirect("/login")

    predictions.delete_one({

        "_id": ObjectId(id),
        "user_id": ObjectId(session["user_id"])

    })

    return redirect("/history")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)