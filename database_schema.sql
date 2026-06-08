PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS carrier_contracts;
DROP TABLE IF EXISTS hotel_contracts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS carriers;
DROP TABLE IF EXISTS hotels;
DROP TABLE IF EXISTS tours;
DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    passport_number TEXT NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'client')),
    client_id INTEGER UNIQUE,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE tours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('cruise', 'resort', 'tourist', 'business', 'exclusive')),
    description TEXT DEFAULT '',
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CHECK (end_date >= start_date)
);

CREATE TABLE routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    visit_order INTEGER NOT NULL CHECK (visit_order > 0),
    description TEXT DEFAULT '',
    FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE
);

CREATE TABLE hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    stars INTEGER NOT NULL CHECK (stars BETWEEN 1 AND 5),
    address TEXT NOT NULL
);

CREATE TABLE carriers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    transport_type TEXT NOT NULL,
    phone TEXT NOT NULL
);

CREATE TABLE hotel_contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id INTEGER NOT NULL,
    contract_number TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    terms TEXT DEFAULT '',
    FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE,
    CHECK (end_date >= start_date)
);

CREATE TABLE carrier_contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carrier_id INTEGER NOT NULL,
    contract_number TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    terms TEXT DEFAULT '',
    FOREIGN KEY (carrier_id) REFERENCES carriers(id) ON DELETE CASCADE,
    CHECK (end_date >= start_date)
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    booking_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'created',
    total_price NUMERIC(10, 2) NOT NULL CHECK (total_price > 0),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (tour_id) REFERENCES tours(id)
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    text TEXT DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (tour_id) REFERENCES tours(id)
);

CREATE INDEX idx_users_login ON users(login);
CREATE INDEX idx_tours_name ON tours(name);
CREATE INDEX idx_tours_type ON tours(type);
CREATE INDEX idx_bookings_client_id ON bookings(client_id);
CREATE INDEX idx_bookings_tour_id ON bookings(tour_id);
CREATE INDEX idx_reviews_tour_id ON reviews(tour_id);
