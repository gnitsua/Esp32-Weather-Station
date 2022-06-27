CREATE TABLE reports (
    id          INTEGER      NOT NULL,
    timestamp   INTEGER      NOT NULL,
    sensor_id   INTEGER      NOT NULL,
    temperature REAL         NOT NULL,
    humidity    REAL         NOT NULL,
    PRIMARY KEY (id)
)