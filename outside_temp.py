import time
from datetime import datetime

import requests as requests

if __name__ == "__main__":
    while(True):
        data = requests.get("https://api.weather.gov/stations/KNYC/observations/latest")


        report = {
            "timestamp": int(datetime.now().timestamp()),
            "sensor_id": 1,
            "temperature":(data.json()["properties"]["temperature"]["value"] * 9/5)+32,
            "humidity":data.json()["properties"]["relativeHumidity"]["value"]
        }

        # report = {'timestamp': 1656287853, 'sensor_id': 1, 'temperature': 80.96, 'humidity': 47.263671578719}
        print(requests.post("http://127.0.0.1:5000/report", json=report).content)
        time.sleep(300)