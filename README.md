# ESP32 weather station
## Introduction

The goal of this project is to implement a low cost temperature logger to track energy efficency in a room. The goals will be to

1. Be able to record temperature data over a 24 hour and 7 day window
2. Recall this data via a smart phone
3. Be able to compare this data against the outdoor temperature

The system will collect weather "reports" which contain temperature and humidity data, which can then be viewed on a simple graph.

The overall system diagram is as follows:

## Parts
### Server
- [Raspberry Pi Model B+](https://www.adafruit.com/product/1914): I am not using the exact model, it shouldn't matter that much
- [HTU21D](https://www.adafruit.com/product/4832) Temperature & Humidity Sensor (Be careful here, in theory the HTU21D-F will work as well, but they require different libraries so you will have to make some code changes)

### Temperature Sensors
- [Adafruit ESP32 Feather V2](https://www.adafruit.com/product/5400) (I also used a V1 board, that works as well)

### Optional for Rasberry Pi Tempurature Sensing
- [QWIIC Cable](https://www.adafruit.com/product/4210) 100mm long
- [QWIIC Shim](https://www.sparkfun.com/products/15794)

## Flask Server
The role of the Flask server is to collect reports the reports from our sensors. We store this data in a few ways but the main two that come to mind are as a CSV and using a SQLite database.
Both of these are file based, so performance is similar, but the main reason to choose the database over a raw file is that we can use the more robust query
language to enable retreiving reports over a variety of timescales rather than a single fixed one. I figured I would want to be able to look at historical data, so this seemed like
 a nice feature.

Our SQLite setup is super simple, we only need a single table and only a few columns. The first major decision
For simplicity, we are going to use epoch timestamps, since SQLite doesn't natively support dates as columns.

The server has two main routes: `/report` which accepts a report from a sensor as a `POST` and `/reports` which retreives saved reports.

One of the first design decisions we need to make is whether to use server time or client time for data submision.
Server time would set the time for the report based on the time the server received the request. Client time, in contrast, allows clients to specify their own time stamp at which the data was connected, which may or may not be the current time. For this project we chose Client time, which has the following pros and cons:
- Pro: Allows sensors to buffer data in the case of a server failure (this has not been implemented yet, but was the main reason for  choosing this method)
- Con: Remote sensors must have a real time clock (the esp32 does)
- Con: Sensors may report incorrect time making graphs inaccurate
- Con: Increases complexity of data contract

Next  we need to make is our primary key. Honestly we could probably just go with an autoincrement key, but since most of our queries are going to be "select * for some time period" I decided to use the report time as part of the key so that this query would be taking advantage of an index. Since we are using `<epoch time><sensor id>` as the primary key for the database, we two main limitations.
- For simplicity's sake we are limiting the number of sensors to 9. This allows us to use a fixed width when we build our key.
- We are using epoch seconds. It is entirely possible however that something like a sensor restart will cause two reports from the same sensor to be submitted in the same second. Instead of adding to our percision, which would effect the entire system, we are just going to toss out any sensor reports who's key already exists in the database.

For retreiving the data, we are going to use `/reports`. We don't need much functionality here, so our only parameters are going to be `start` and `end`.
This will allow us to grab parts of our data

## Running the project
To start the server run the following
```
python3 -m flask run --host=0.0.0.0
```
