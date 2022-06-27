# ESP32 weather station
The goal of this project is to create an affordable temperature recording system with multiple remote sensors.
The overall system diagram is as follows:


The system will collect weather "reports" which contain temperature and humidity data, which can then be viewed on a simple graph.

## Flask Server
The role of the Flask server is to collect reports the reports from our sensors. We store this data in a few ways but the main two that come to mind are as a CSV and using a SQLite database.
Both of these are file based, so performance is similar, but the main reason to choose the database over a raw file is that we can use the more robust query
language to enable retreiving reports over a variety of timescales rather than a single fixed one. I figured I would want to be able to look at historical data, so this seemed like
 a nice feature.

Our SQLite setup is super simple, we only need a single table and only a few columns. The first major decision we need to make is our primary key.
Honestly we could probably just go with an autoincrement key, but since most of our queries are going to be "select * for some time period" I decided to use the report time as part of the key so that this query would be taking advantage of an index.
For simplicity, we are going to use epoch timestamps, since SQLite doesn't natively support dates as columns.