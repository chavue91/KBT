-- all fish caught in tournament with status.

SELECT 
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
ORDER BY t.tournament_date, u.last_name, f.fish_length DESC;

-- leader board

SELECT
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
ORDER BY t.tournament_date, total_length_inches DESC;