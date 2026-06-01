import pandas as pd
import random

data = []

for i in range(1000):

    study_hours = random.randint(1, 10)
    attendance = random.randint(50, 100)
    previous_score = random.randint(40, 95)
    sleep_hours = random.randint(4, 10)
    assignments = random.randint(0, 10)
    internet_usage = random.randint(1, 8)

    final_score = (
        study_hours * 4
        + attendance * 0.3
        + previous_score * 0.4
        + sleep_hours * 1
        + assignments * 1.5
        - internet_usage * 1.2
    )

    final_score = max(0, min(100, round(final_score)))

    data.append([
        study_hours,
        attendance,
        previous_score,
        sleep_hours,
        assignments,
        internet_usage,
        final_score
    ])

df = pd.DataFrame(data, columns=[
    "StudyHours",
    "Attendance",
    "PreviousScore",
    "SleepHours",
    "AssignmentsCompleted",
    "InternetUsage",
    "FinalScore"
])

df.to_csv("student_scores.csv", index=False)

print("Dataset Generated Successfully")