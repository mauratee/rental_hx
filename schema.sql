DROP TABLE IF EXISTS apartments;

CREATE TABLE apartments (
    id INTEGER PRIMARY KEY,
    housenumber TEXT NOT NULL,
    street TEXT NOT NULL,
    borough TEXT NOT NULL,
    unitnumber TEXT,
    postalcode TEXT
);
