import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib
from sklearn.metrics import r2_score, mean_absolute_error


def main():
    # ensure model directory exists
    os.makedirs("model", exist_ok=True)

    # load dataset (project contains student_scores.csv)
    df = pd.read_csv("student_scores.csv")

    # map dataset columns to canonical names used by the model
    rename_map = {
        "StudyHours": "hours",
        "Attendance": "attendance",
        "PreviousScore": "previous",
        "SleepHours": "sleep_hours",
        "AssignmentsCompleted": "assignments",
        "InternetUsage": "internet_usage",
        "FinalScore": "score",
    }
    df = df.rename(columns=rename_map)

    # keep only required columns (drop rows with missing values)
    required = list(rename_map.values())
    df = df[required].dropna()

    X = df[["hours", "attendance", "previous", "sleep_hours", "assignments", "internet_usage"]]
    y = df["score"]

    # scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # train/test split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # model
    model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    # evaluate
    preds = model.predict(X_test)
    r2 = r2_score(y_test, preds)
    mae = mean_absolute_error(y_test, preds)
    print(f"R2 score: {r2:.4f}")
    print(f"MAE: {mae:.4f}")

    # save artifacts
    joblib.dump(model, "model/score_model.pkl")
    joblib.dump(scaler, "model/scaler.pkl")
    print("Saved model to model/score_model.pkl and scaler to model/scaler.pkl")


if __name__ == "__main__":
    main()