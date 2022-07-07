import time

from flask import Flask, send_from_directory
from flask import request
import sqlite3
from flask import g

app = Flask(__name__)

DATABASE = 'database.db'

# DB helper functions, mostly from the Flask documentation (https://flask.palletsprojects.com/en/2.1.x/patterns/sqlite3/)
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# This is our main logic for submitting reports to the database
def write_report(timestamp: int, sensor_id: int, temperature: float, humidity: float):
    get_db().execute("insert into reports values(?, ?, ?, ?, ?)", [
        get_key(timestamp, sensor_id),
        timestamp,
        sensor_id,
        temperature,
        humidity
    ])
    get_db().commit()

# Our key is "<time><sensor_id>". This allows for efficent queries for time ranges but prevents collisions when multiple sensors report in the same second
def get_key(time: int, sensor_id: float):
    assert (sensor_id < 10)  # We are going to make the assumtion that we have less than 10 sensors so we can use a fixed offset
    return time * 10 + sensor_id


# Routes to support the frontend. We need to serve the index html as well as our static JS
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Our application routes
# We will submit our condition reports via a post to this endpoint
# The input json should be of the format {"timestamp": <epoch time>, "sensor_id": <int>, "temperature": <float>, "humidity": <float>}
@app.route('/report', methods=['POST'])
def report():
    data = request.get_json(force=True)
    try:
        write_report(
            int(data["timestamp"]),
            int(data["sensor_id"]),
            float(data["temperature"]),
            float(data["humidity"])
        )
    except sqlite3.IntegrityError as e:
        # We don't need to support more than one report per sensor per second
        # When this happens we could choose to keep either the first or second report
        # In this case we are choosing to keep the first one
        # We will still return success in this case since this dedupe logic is an implementation detail
        print("Two records returned with the same key, dropping report %s" % (data))

    return {"status": "Success"}

# The reports endpoint will return all points by default, but the scope can be limited to a timeframe by supplying "start" and "end" in epoch time
@app.route('/reports', methods=['GET'])
def reports():
    start = request.args.get('start', default=0, type=int)  # When no start is provided default to 0 (which is 01/01/1970)
    end = request.args.get('end', int(time.time()), type=int)  # When no end is provided default to current time
    start_key = start * 10 # Add our key padding
    end_key = end * 10 + 9

    reports = query_db('select * from reports where id >= ? and id <= ?', [start_key, end_key])
    return {"reports": reports}


# From the Flask documentation
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
