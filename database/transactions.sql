-- ============================================================
-- TRANSACTION DEMO — Batch Fish Submission
-- ============================================================
-- Scenario:
--   An angler submits multiple fish catches at once during a
--   tournament. Each fish is inserted individually with a
--   SAVEPOINT before it. If a single insert fails (bad length,
--   invalid species, etc.), we ROLLBACK TO that savepoint and
--   skip that fish — without losing the ones that succeeded.
--   At the end we COMMIT everything that passed.
--
-- Angler:       Derek Holloway (user_id = 3)
-- Tournament:   Lake Minnetonka (tournament_id = 1)
-- ============================================================

BEGIN;

-- ── Fish 1: valid submission ─────────────────────────────────
SAVEPOINT before_fish_1;

INSERT INTO fish (livewell_id, species, fish_length, status)
SELECT lw.livewell_id, 'Largemouth Bass', 13.50, 'PENDING'
FROM livewell lw
JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
WHERE ta.angler_user_id = 3 AND ta.tournament_id = 1;

-- Fish 1 looks good, release the savepoint
RELEASE SAVEPOINT before_fish_1;


-- ── Fish 2: invalid submission (fish_length out of range) ────
SAVEPOINT before_fish_2;

INSERT INTO fish (livewell_id, species, fish_length, status)
SELECT lw.livewell_id, 'Largemouth Bass', 150.00, 'PENDING'  -- violates CHECK constraint (max 99.99)
FROM livewell lw
JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
WHERE ta.angler_user_id = 3 AND ta.tournament_id = 1;

-- Fish 2 failed — roll back only this insert, keep fish 1
ROLLBACK TO SAVEPOINT before_fish_2;
RELEASE SAVEPOINT before_fish_2;


-- ── Fish 3: valid submission ─────────────────────────────────
SAVEPOINT before_fish_3;

INSERT INTO fish (livewell_id, species, fish_length, status)
SELECT lw.livewell_id, 'Smallmouth Bass', 11.25, 'PENDING'
FROM livewell lw
JOIN tournament_anglers ta ON lw.tournament_entry_id = ta.tournament_angler_id
WHERE ta.angler_user_id = 3 AND ta.tournament_id = 1;

-- Fish 3 looks good, release the savepoint
RELEASE SAVEPOINT before_fish_3;


-- ── Commit all successful inserts ───────────────────────────
-- Fish 1 and Fish 3 are committed. Fish 2 was rolled back.
COMMIT;