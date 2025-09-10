DROP TABLE IF EXISTS rep_geography_map;
DROP TABLE IF EXISTS geography;
DROP TABLE IF EXISTS representatives;


CREATE TABLE geography (
    zip_code VARCHAR(5) PRIMARY KEY,
    city VARCHAR(255),
    state VARCHAR(255),
    district VARCHAR(255)
);

CREATE TABLE representatives (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(255),
    branch VARCHAR(50)
);

CREATE TABLE rep_geography_map (
    representative_id INTEGER NOT NULL REFERENCES representatives(id) ON DELETE CASCADE,
    geography_zip_code VARCHAR(5) NOT NULL REFERENCES geography(zip_code) ON DELETE CASCADE,
    PRIMARY KEY (representative_id, geography_zip_code)
);
