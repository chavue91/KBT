-- ============================================================
-- TEST DATA POPULATION SCRIPT (PostgreSQL)
-- Uses CTEs with RETURNING to handle GENERATED ALWAYS AS IDENTITY
-- ============================================================
 
-- ── Users + Directors ────────────────────────────────────────
WITH inserted_directors AS (
    INSERT INTO users (first_name, last_name, email, phone_number) VALUES
    ('Robert', 'Tanner', 'robert.tanner@email.com', '612-555-0101'),
    ('Linda',  'Marsh',  'linda.marsh@email.com',   '651-555-0102')
    RETURNING user_id
)
INSERT INTO directors (user_id)
SELECT user_id FROM inserted_directors;
 
-- ── Users + Anglers ──────────────────────────────────────────
WITH inserted_anglers AS (
    INSERT INTO users (first_name, last_name, email, phone_number) VALUES
    ('Derek',    'Holloway', 'derek.holloway@email.com',  '763-555-0103'),
    ('Samantha', 'Pike',     'samantha.pike@email.com',   '952-555-0104'),
    ('Carlos',   'Vega',     'carlos.vega@email.com',     '218-555-0105'),
    ('Brenda',   'Kowalski', 'brenda.kowalski@email.com', '320-555-0106'),
    ('Tom',      'Braddock', 'tom.braddock@email.com',    '507-555-0107'),
    ('Nancy',    'Elrod',    'nancy.elrod@email.com',     '715-555-0108')
    RETURNING user_id
)
INSERT INTO anglers (user_id)
SELECT user_id FROM inserted_anglers;
 
-- ── Tournaments ──────────────────────────────────────────────
INSERT INTO tournaments (
    director_user_id, body_of_water,
    street_address, city, state_code, postal_code,
    tournament_date, start_time, end_time
)
SELECT u.user_id,
       t.body_of_water, t.street_address, t.city, t.state_code, t.postal_code,
       t.tournament_date, t.start_time, t.end_time
FROM (
    SELECT user_id, ROW_NUMBER() OVER (ORDER BY user_id) AS rn
    FROM directors
) u
JOIN (
    VALUES
    (1, 'Lake Minnetonka', '100 Lakeshore Dr', 'Wayzata', 'MN', '55391', DATE '2025-06-14', TIME '07:00:00', TIME '13:00:00'),
    (1, 'Mille Lacs Lake', '200 Bass Rd',       'Onamia',  'MN', '56359', DATE '2025-07-19', TIME '06:30:00', TIME '12:30:00'),
    (2, 'Lake Vermilion',  '45 Walleye Way',    'Tower',   'MN', '55790', DATE '2025-08-02', TIME '08:00:00', TIME '14:00:00')
) AS t(director_rn, body_of_water, street_address, city, state_code, postal_code, tournament_date, start_time, end_time)
ON u.rn = t.director_rn;
 
-- ── Tournament Anglers ───────────────────────────────────────
INSERT INTO tournament_anglers (tournament_id, angler_user_id)
SELECT t.tournament_id, a.user_id
FROM (
    SELECT user_id, ROW_NUMBER() OVER (ORDER BY user_id) AS rn FROM anglers
) a
JOIN (
    SELECT tournament_id, ROW_NUMBER() OVER (ORDER BY tournament_id) AS rn FROM tournaments
) t ON (
    (t.rn = 1 AND a.rn IN (1,2,3,4)) OR
    (t.rn = 2 AND a.rn IN (3,5,6))   OR
    (t.rn = 3 AND a.rn IN (1,4,5,6))
);
 
-- ── Livewells ────────────────────────────────────────────────
INSERT INTO livewell (tournament_entry_id)
SELECT tournament_angler_id FROM tournament_anglers;
 
-- ── Fish ─────────────────────────────────────────────────────
INSERT INTO fish (livewell_id, species, fish_length, status)
SELECT l.livewell_id, f.species, f.fish_length, f.status
FROM livewell l
JOIN tournament_anglers ta ON ta.tournament_angler_id = l.tournament_entry_id
JOIN (
    SELECT user_id, ROW_NUMBER() OVER (ORDER BY user_id) AS rn FROM anglers
) a ON a.user_id = ta.angler_user_id
JOIN (
    SELECT tournament_id, ROW_NUMBER() OVER (ORDER BY tournament_id) AS t_rn FROM tournaments
) t ON t.tournament_id = ta.tournament_id
JOIN (
    VALUES
    (1, 1, 'Largemouth Bass', 14.50::DECIMAL, 'APPROVED'),
    (1, 1, 'Largemouth Bass', 12.75::DECIMAL, 'APPROVED'),
    (1, 1, 'Smallmouth Bass', 11.00::DECIMAL, 'PENDING'),
    (2, 1, 'Largemouth Bass', 16.25::DECIMAL, 'APPROVED'),
    (2, 1, 'Walleye',         18.00::DECIMAL, 'APPROVED'),
    (3, 1, 'Largemouth Bass', 13.50::DECIMAL, 'REJECTED'),
    (3, 1, 'Smallmouth Bass', 10.25::DECIMAL, 'PENDING'),
    (4, 1, 'Largemouth Bass', 15.00::DECIMAL, 'APPROVED'),
    (3, 2, 'Walleye',         20.50::DECIMAL, 'APPROVED'),
    (3, 2, 'Walleye',         19.75::DECIMAL, 'APPROVED'),
    (3, 2, 'Northern Pike',   24.00::DECIMAL, 'APPROVED'),
    (5, 2, 'Walleye',         17.25::DECIMAL, 'PENDING'),
    (5, 2, 'Northern Pike',   22.50::DECIMAL, 'PENDING'),
    (6, 2, 'Walleye',         15.50::DECIMAL, 'APPROVED'),
    (1, 3, 'Largemouth Bass', 13.00::DECIMAL, 'APPROVED'),
    (1, 3, 'Smallmouth Bass', 12.00::DECIMAL, 'REJECTED'),
    (4, 3, 'Northern Pike',   26.75::DECIMAL, 'APPROVED'),
    (4, 3, 'Walleye',         21.00::DECIMAL, 'APPROVED'),
    (5, 3, 'Largemouth Bass', 14.00::DECIMAL, 'PENDING'),
    (6, 3, 'Smallmouth Bass', 11.50::DECIMAL, 'APPROVED'),
    (6, 3, 'Largemouth Bass', 16.00::DECIMAL, 'APPROVED')
) AS f(angler_rn, tournament_rn, species, fish_length, status)
ON a.rn = f.angler_rn AND t.t_rn = f.tournament_rn;
 
-- ── Fish Photos (one per livewell, for the first fish only) ──
INSERT INTO fish_photo (fish_id, photo_url, uploaded_at)
SELECT f.fish_id,
       'https://storage.example.com/fish/fish-' || f.fish_id || '.jpg',
       CURRENT_TIMESTAMP
FROM (
    SELECT fish_id,
           ROW_NUMBER() OVER (PARTITION BY livewell_id ORDER BY fish_id) AS rn
    FROM fish
) f
WHERE f.rn = 1;