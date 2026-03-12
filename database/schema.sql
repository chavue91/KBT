DROP TABLE IF EXISTS fish_photo;
DROP TABLE IF EXISTS fish;
DROP TABLE IF EXISTS livewell;
DROP TABLE IF EXISTS tournament_anglers;
DROP TABLE IF EXISTS tournaments;
DROP TABLE IF EXISTS anglers;
DROP TABLE IF EXISTS directors;
DROP TABLE IF EXISTS users;


CREATE TABLE users (
user_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
first_name VARCHAR(30) NOT NULL,
last_name VARCHAR(30) NOT NULL,
email VARCHAR(100) NOT NULL UNIQUE,
phone_number VARCHAR(20)
);

CREATE TABLE directors (
user_id INT PRIMARY KEY,

FOREIGN KEY (user_id) REFERENCES users(user_id)
	ON DELETE CASCADE
);

CREATE TABLE anglers (
user_id INT PRIMARY KEY,

FOREIGN KEY (user_id) REFERENCES users(user_id)
	ON DELETE CASCADE
);

CREATE TABLE tournaments (
tournament_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
director_user_id INT NOT NULL,
body_of_water VARCHAR(30) NOT NULL,
street_address VARCHAR(30),
city VARCHAR(30) NOT NULL,
state_code CHAR(2) NOT NULL,
postal_code CHAR(5) NOT NULL,
tournament_date DATE NOT NULL DEFAULT CURRENT_DATE,
start_time TIME NOT NULL DEFAULT '08:00:00',
end_time TIME NOT NULL DEFAULT '14:00:00',

CONSTRAINT fk_tournament_director
FOREIGN KEY (director_user_id) REFERENCES directors(user_id)
	ON DELETE CASCADE
);

CREATE TABLE tournament_anglers (
tournament_angler_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
tournament_id INT NOT NULL,
angler_user_id INT NOT NULL,

FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id)
	ON DELETE CASCADE,
FOREIGN KEY (angler_user_id) REFERENCES anglers(user_id)
	ON DELETE CASCADE,
UNIQUE (tournament_id, angler_user_id)
);

CREATE TABLE livewell (
livewell_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
tournament_entry_id INT NOT NULL UNIQUE,

CONSTRAINT fk_livewell_entry
FOREIGN KEY (tournament_entry_id) REFERENCES tournament_anglers(tournament_angler_id)
	ON DELETE CASCADE
);

CREATE TABLE fish (
fish_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
livewell_id INT NOT NULL,
species VARCHAR(30) NOT NULL,
fish_length DECIMAL(4,2) NOT NULL
	CHECK (fish_length >= 0 AND fish_length <= 99.99),
status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
	CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),

FOREIGN KEY (livewell_id) REFERENCES livewell(livewell_id)
	ON DELETE CASCADE
);

CREATE TABLE fish_photo (
fish_id INT PRIMARY KEY,
photo_url VARCHAR(255) NOT NULL UNIQUE,
uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

FOREIGN KEY (fish_id) REFERENCES fish(fish_id)
	ON DELETE CASCADE
);