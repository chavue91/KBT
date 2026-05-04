-- all fish caught in tournament with status.

SELECT 
	t.tournament_id,
    u.first_name,
    u.last_name,
    t.body_of_water,
    t.tournament_date,
    f.species,
    f.fish_length,
    f.status
FROM fish f
JOIN livewell lw ON f.livewell_id = lw.livewell_id
JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
JOIN anglers a ON ta.angler_user_id = a.user_id
JOIN users u ON a.user_id = u.user_id
JOIN tournaments t ON ta.tournament_id = t.tournament_id
ORDER BY t.tournament_id, u.last_name, f.fish_length DESC;

-- leader board

SELECT
	t.tournament_id,
    u.first_name,
    u.last_name,
    t.body_of_water,
    t.tournament_date,
    COUNT(f.fish_id) AS approved_fish_count,
    SUM(f.fish_length) AS total_length_inches
FROM fish f
JOIN livewell lw ON f.livewell_id = lw.livewell_id
JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
JOIN anglers a ON ta.angler_user_id = a.user_id
JOIN users u ON a.user_id = u.user_id
JOIN tournaments t ON ta.tournament_id = t.tournament_id
WHERE f.status = 'APPROVED'
GROUP BY u.user_id, u.first_name, u.last_name, t.tournament_id, t.body_of_water, t.tournament_date
ORDER BY t.tournament_id, total_length_inches DESC;

-- ────────────────────────────────────────────────────────────
-- BASIC SELECT QUERIES
-- ────────────────────────────────────────────────────────────
 
-- 1. All users in the system
SELECT user_id, first_name, last_name, email, phone_number
FROM users;
 
-- 2. All tournaments sorted by date
SELECT tournament_id, body_of_water, city, state_code, tournament_date, start_time, end_time
FROM tournaments
ORDER BY tournament_date;
 
-- 3. All fish with PENDING status
SELECT fish_id, livewell_id, species, fish_length, status
FROM fish
WHERE status = 'PENDING';
 
-- 4. All fish longer than 18 inches
SELECT fish_id, species, fish_length, status
FROM fish
WHERE fish_length > 18.00
ORDER BY fish_length DESC;
 
-- 5. All tournaments held in Minnesota
SELECT tournament_id, body_of_water, city, tournament_date
FROM tournaments
WHERE state_code = 'MN'
ORDER BY tournament_date;
 
 
-- ────────────────────────────────────────────────────────────
-- JOIN QUERIES
-- ────────────────────────────────────────────────────────────
 
-- 1. (INNER) All anglers with their tournament registrations
SELECT u.first_name, u.last_name, t.body_of_water, t.tournament_date
FROM users u
INNER JOIN tournament_anglers ta ON u.user_id = ta.angler_user_id
INNER JOIN tournaments t ON ta.tournament_id = t.tournament_id
ORDER BY t.tournament_date, u.last_name;
 
-- 2. (INNER) All fish with their angler and tournament
SELECT u.first_name, u.last_name, t.body_of_water, f.species, f.fish_length, f.status
FROM fish f
INNER JOIN livewell lw ON f.livewell_id = lw.livewell_id
INNER JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
INNER JOIN users u ON ta.angler_user_id = u.user_id
INNER JOIN tournaments t ON ta.tournament_id = t.tournament_id;
 
-- 3. (LEFT OUTER) All anglers including those with no fish catches
SELECT u.first_name, u.last_name, f.species, f.fish_length, f.status
FROM users u
INNER JOIN anglers a ON u.user_id = a.user_id
INNER JOIN tournament_anglers ta ON a.user_id = ta.angler_user_id
INNER JOIN livewell lw ON ta.tournament_angler_id = lw.tournament_entry_id
LEFT JOIN fish f ON lw.livewell_id = f.livewell_id
ORDER BY u.last_name;
 
-- 4. (LEFT OUTER) All fish and their photos, including fish without photos
SELECT f.fish_id, f.species, f.fish_length, f.status, fp.photo_url, fp.uploaded_at
FROM fish f
LEFT JOIN fish_photo fp ON f.fish_id = fp.fish_id
ORDER BY f.fish_id;
 
-- 5. (SELF JOIN) Users who share the same last name
SELECT a.user_id AS user_a, a.last_name, a.first_name,
       b.user_id AS user_b, b.first_name AS first_name_b
FROM users a
INNER JOIN users b ON a.last_name = b.last_name AND a.user_id < b.user_id;
 
-- all fish caught in tournament with status.

SELECT 
	t.tournament_id,
    u.first_name,
    u.last_name,
    t.body_of_water,
    t.tournament_date,
    f.species,
    f.fish_length,
    f.status
FROM fish f
JOIN livewell lw ON f.livewell_id = lw.livewell_id
JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
JOIN anglers a ON ta.angler_user_id = a.user_id
JOIN users u ON a.user_id = u.user_id
JOIN tournaments t ON ta.tournament_id = t.tournament_id
ORDER BY t.tournament_id, u.last_name, f.fish_length DESC;
-- ────────────────────────────────────────────────────────────
-- GROUP BY + AGGREGATE QUERIES
-- ────────────────────────────────────────────────────────────
 
-- 1. Total fish caught per species across all tournaments
SELECT species,
       COUNT(*) AS total_caught,
       ROUND(AVG(fish_length), 2) AS avg_length,
       MAX(fish_length) AS longest
FROM fish
GROUP BY species
ORDER BY total_caught DESC;
 
-- 2. Number of fish per approval status
SELECT status,
       COUNT(*) AS fish_count
FROM fish
GROUP BY status
ORDER BY fish_count DESC;
 
-- 3. Leaderboard — total approved catch length per angler per tournament
-- leader board

SELECT
	t.tournament_id,
    u.first_name,
    u.last_name,
    t.body_of_water,
    t.tournament_date,
    COUNT(f.fish_id) AS approved_fish_count,
    SUM(f.fish_length) AS total_length_inches
FROM fish f
JOIN livewell lw ON f.livewell_id = lw.livewell_id
JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
JOIN anglers a ON ta.angler_user_id = a.user_id
JOIN users u ON a.user_id = u.user_id
JOIN tournaments t ON ta.tournament_id = t.tournament_id
WHERE f.status = 'APPROVED'
GROUP BY u.user_id, u.first_name, u.last_name, t.tournament_id, t.body_of_water, t.tournament_date
ORDER BY t.tournament_id, total_length_inches DESC;
 
 
-- ────────────────────────────────────────────────────────────
-- SUBQUERIES
-- ────────────────────────────────────────────────────────────
 
-- 1. (Scalar) Fish longer than the overall average fish length
SELECT fish_id, species, fish_length, status
FROM fish
WHERE fish_length > (SELECT AVG(fish_length) FROM fish)
ORDER BY fish_length DESC;
 
-- 2. (Nested) Anglers who have participated in more than one tournament
SELECT u.first_name, u.last_name
FROM users u
WHERE u.user_id IN (
    SELECT angler_user_id
    FROM tournament_anglers
    GROUP BY angler_user_id
    HAVING COUNT(tournament_id) > 1
)
ORDER BY u.last_name;
 
-- 3. (Correlated) Anglers whose longest fish exceeds the average longest fish across all anglers
SELECT u.first_name, u.last_name
FROM users u
INNER JOIN anglers a ON u.user_id = a.user_id
WHERE (
    SELECT MAX(f.fish_length)
    FROM fish f
    INNER JOIN livewell lw ON f.livewell_id = lw.livewell_id
    INNER JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
    WHERE ta.angler_user_id = u.user_id
) > (
    SELECT AVG(max_length) FROM (
        SELECT MAX(f2.fish_length) AS max_length
        FROM fish f2
        INNER JOIN livewell lw2 ON f2.livewell_id = lw2.livewell_id
        INNER JOIN tournament_anglers ta2 ON lw2.tournament_entry_id = ta2.tournament_angler_id
        GROUP BY ta2.angler_user_id
    ) sub
);
 
 
-- ────────────────────────────────────────────────────────────
-- VIEW DEFINITIONS
-- ────────────────────────────────────────────────────────────
 
-- 1. Angler catch summary view
CREATE VIEW vw_angler_catch_summary AS
SELECT u.user_id, u.first_name, u.last_name,
       t.tournament_id, t.body_of_water, t.tournament_date,
       COUNT(f.fish_id) AS total_fish,
       SUM(CASE WHEN f.status = 'APPROVED' THEN f.fish_length ELSE 0 END) AS approved_total_length,
       MAX(f.fish_length) AS longest_fish
FROM users u
INNER JOIN tournament_anglers ta ON u.user_id = ta.angler_user_id
INNER JOIN tournaments t ON ta.tournament_id = t.tournament_id
INNER JOIN livewell lw ON ta.tournament_angler_id = lw.tournament_entry_id
LEFT JOIN fish f ON lw.livewell_id = f.livewell_id
GROUP BY u.user_id, u.first_name, u.last_name, t.tournament_id, t.body_of_water, t.tournament_date;
 
-- 2. Fish with photo status view
CREATE VIEW vw_fish_photo_status AS
SELECT f.fish_id, f.species, f.fish_length, f.status,
       CASE WHEN fp.fish_id IS NOT NULL THEN 'Yes' ELSE 'No' END AS has_photo,
       fp.photo_url,
       u.first_name, u.last_name,
       t.body_of_water, t.tournament_date
FROM fish f
INNER JOIN livewell lw ON f.livewell_id = lw.livewell_id
INNER JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
INNER JOIN users u ON ta.angler_user_id = u.user_id
INNER JOIN tournaments t ON ta.tournament_id = t.tournament_id
LEFT JOIN fish_photo fp ON f.fish_id = fp.fish_id;