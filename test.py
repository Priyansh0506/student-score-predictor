import requests
from bs4 import BeautifulSoup

data = {
    "hours": 6,
    "attendance": 85,
    "previous": 72,
    "sleep_hours": 7,
    "assignments": 8,
    "internet_usage": 3
}

response = requests.post("http://127.0.0.1:5001/predict", data=data)
print(response.text)
