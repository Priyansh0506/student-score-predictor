import os  
from flask import Flask, render_template, request, redirect, url_for, session
import joblib
...
from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import sqlite3
from sklearn.metrics import r2_score, mean_absolute_error
import pandas as pd

app = Flask(__name__)
app.secret_key = "supersecretkey"

model = joblib.load("model/score_model.pkl")


# -----------------------------
# DATABASE INIT
# -----------------------------
def init_db():
    conn = sqlite3.connect("predictions.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hours REAL,
            attendance REAL,
            previous REAL,
            sleep_hours REAL,
            assignments REAL,
            internet_usage REAL,
            score REAL,
            risk TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -----------------------------
# LOGIN PAGE
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("predictions.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return "Invalid login ❌"

    return render_template("login.html")


# -----------------------------
# REGISTER PAGE
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("predictions.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    model_r2 = None
    model_mae = None
    try:
        model = joblib.load("model/score_model.pkl")
        scaler = joblib.load("model/scaler.pkl")
        df = pd.read_csv("student_scores.csv")
        df = df.rename(columns={
            "StudyHours": "hours",
            "Attendance": "attendance",
            "PreviousScore": "previous",
            "SleepHours": "sleep_hours",
            "AssignmentsCompleted": "assignments",
            "InternetUsage": "internet_usage",
            "FinalScore": "score",
        })
        X = df[["hours", "attendance", "previous", "sleep_hours", "assignments", "internet_usage"]].dropna()
        y = df["score"][X.index]
        Xs = scaler.transform(X)
        preds = model.predict(Xs)
        model_r2 = round(r2_score(y, preds), 4)
        model_mae = round(mean_absolute_error(y, preds), 4)
    except Exception:
        model_r2 = None
        model_mae = None

    return render_template("index.html", model_r2=model_r2, model_mae=model_mae)


# -----------------------------
# PREDICT
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))

    hours = float(request.form.get("hours", 0))
    attendance = float(request.form.get("attendance", 0))
    previous = float(request.form.get("previous", 0))
    sleep_hours = float(request.form.get("sleep_hours", 0))
    assignments = float(request.form.get("assignments", 0))
    internet_usage = float(request.form.get("internet_usage", 0))

    result = model.predict([[
        hours, attendance, previous,
        sleep_hours, assignments, internet_usage
    ]])

    score = float(result[0])

    if score < 50:
        risk = "High Risk"
    elif score < 75:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    # ✅ SUGGESTIONS LOGIC
    suggestions = []
    if hours < 5:
        suggestions.append("📚 Study hours badha — kam se kam 5-6 ghante roz padh")
    if attendance < 75:
        suggestions.append("🏫 Attendance 75% se upar rakh — classes mat miss kar")
    if sleep_hours < 6:
        suggestions.append("😴 Neend 6-8 ghante lena zaroori hai — brain rest karta hai")
    if internet_usage > 4:
        suggestions.append("📱 Phone/internet 4 ghante se kam use kar — distraction kam hoga")
    if assignments < 7:
        suggestions.append("✏️ Assignments complete kar — practice se concepts clear hote hain")
    if previous < 50:
        suggestions.append("📝 Previous score kam hai — weak subjects pe extra focus kar")
    if not suggestions:
        suggestions.append("🌟 Sab kuch sahi hai — aise hi chalta reh, Top performer ban jayega!")

    # ✅ WHAT-IF: 2 ghante aur padhe toh?
    whatif_result = model.predict([[
        hours + 2, attendance, previous,
        sleep_hours, assignments, internet_usage
    ]])
    whatif_score = round(float(whatif_result[0]), 2)

    conn = sqlite3.connect("predictions.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO history (
            hours, attendance, previous, sleep_hours,
            assignments, internet_usage, score, risk
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (hours, attendance, previous, sleep_hours, assignments, internet_usage, score, risk))
    conn.commit()
    conn.close()

    # Load model metrics for display
    model_r2 = None
    model_mae = None
    try:
        scaler = joblib.load("model/scaler.pkl")
        df = pd.read_csv("student_scores.csv")
        df = df.rename(columns={
            "StudyHours": "hours", "Attendance": "attendance", "PreviousScore": "previous",
            "SleepHours": "sleep_hours", "AssignmentsCompleted": "assignments",
            "InternetUsage": "internet_usage", "FinalScore": "score",
        })
        X = df[["hours", "attendance", "previous", "sleep_hours", "assignments", "internet_usage"]].dropna()
        y = df["score"][X.index]
        Xs = scaler.transform(X)
        preds = model.predict(Xs)
        model_r2 = round(r2_score(y, preds), 4)
        model_mae = round(mean_absolute_error(y, preds), 4)
    except Exception:
        pass

    return render_template(
        "index.html",
        prediction=round(score, 2),
        risk=risk,
        suggestions=suggestions,
        whatif_score=whatif_score,
        hours=hours,
        model_r2=model_r2,
        model_mae=model_mae
    )


# -----------------------------
# HISTORY
# -----------------------------
@app.route("/history")
def history():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("predictions.db")
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY id DESC")
    data = c.fetchall()
    conn.close()

    low = sum(1 for r in data if r[8] == "Low Risk")
    medium = sum(1 for r in data if r[8] == "Medium Risk")
    high = sum(1 for r in data if r[8] == "High Risk")

    return render_template("history.html", data=data, low=low, medium=medium, high=high)


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))