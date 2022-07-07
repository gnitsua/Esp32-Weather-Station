/***************************************************
  This is an example for the HTU21D-F Humidity & Temp Sensor

  Designed specifically to work with the HTU21D-F sensor from Adafruit
  ----> https://www.adafruit.com/products/1899

  These displays use I2C to communicate, 2 pins are required to
  interface
 ****************************************************/

#include <Wire.h>
#include "Adafruit_HTU31D.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include "time.h"
#include "sntp.h"

// Connect Vin to 3-5VDC
// Connect GND to ground
// Connect SCL to I2C clock pin (A5 on UNO)
// Connect SDA to I2C data pin (A4 on UNO)

//#define SDA1 26
//#define SCL1 25

// Wifi config
const char* ssid       = "the_overlook";
const char* password   = "Apartment52Bravo";

// Time setup (from example
const char* ntpServer1 = "pool.ntp.org";
const char* ntpServer2 = "time.nist.gov";
const long  gmtOffset_sec = 3600;
const int   daylightOffset_sec = 3600;

// https://sites.google.com/a/usapiens.com/opnode/time-zones
const char* time_zone = "CET-1CEST,M3.5.0,M10.5.0/3";  // TimeZone rule for Europe/Rome including daylight adjustment rules (optional)

// https://randomnerdtutorials.com/epoch-unix-time-esp32-arduino/
unsigned long getEpochTime()
{
  time_t now;
  struct tm timeinfo;
  if(!getLocalTime(&timeinfo)){
    Serial.println("No time available (yet)");
    return(0);
  }
  Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");
  return time(&now);
}

// Sensor setup
Adafruit_HTU31D htu = Adafruit_HTU31D();

// Server Setup
const char* serverName = "http://192.168.0.34:5000/report";
//const int sensorId = 3; // green
const int sensorId = 4; // pink

void setup() {
  Serial.begin(115200);
  Serial.println("HTU21D-F test");

  // Setup wifi
  Serial.printf("Connecting to %s ", ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }
  Serial.println(" CONNECTED");

  // Set up RTC, based on example
  sntp_servermode_dhcp(1);    // (optional)
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer1, ntpServer2);

  // Set up the HTU21DF
  if (!htu.begin()) {
      Serial.println("Couldn't find sensor!");
  }
}

void loop() {
    //delay(3000); // Put the delay first because on the first iteration we need some
    delay(300000);
    
    // Fetch the data from the sensor
    sensors_event_t humidity, temp;
    htu.getEvent(&humidity, &temp);// populate temp and humidity objects with fresh data
  
    // Build the report JSON
    String report = "{\"timestamp\":";
    report += getEpochTime();
    report += ",\"sensor_id\":";
    report += sensorId;
    report += ",\"temperature\":";
    report += (temp.temperature * 9 / 5) + 32;
    report += ",\"humidity\":";
    report += humidity.relative_humidity;
    report += "}";
    Serial.println("Submitting Report");
    Serial.println(report);

    // Now post the report to our server
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(report);
    Serial.println("Submitted Report");
    Serial.println(httpResponseCode);
}
