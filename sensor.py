
import board
import time
from datetime import datetime
import adafruit_htu31d
import requests


if __name__ == "__main__":
    i2c = board.I2C()
    htu = adafruit_htu31d.HTU31D(i2c)
    
    
    while(True):
        temp, hum = htu.measurements
        temp_f = temp * (9/5) + 32
        
        report = {
            "timestamp": int(datetime.now().timestamp()),
            "sensor_id": 2,
            "temperature": temp_f,
            "humidity":hum
        }

        # report = {'timestamp': 1656287853, 'sensor_id': 1, 'temperature': 80.96, 'humidity': 47.263671578719}
        print(requests.post("http://127.0.0.1:5000/report", json=report).content)
        print("Temp: %0.1f F" % (temp_f))
        print("Hum: %0.1f %%" % hum)
        #with open("temp-%s.csv"%(datetime.now().strftime("%m-%d-%y")),"a") as file:
        #    file.write("%s,%0.2f,%0.2f\n"%(datetime.now().isoformat(),temp_f,hum))
        time.sleep(300)
