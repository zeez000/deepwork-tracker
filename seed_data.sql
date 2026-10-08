BEGIN TRANSACTION;

INSERT INTO sessions (title, goal, scheduled_duration, status)
SELECT
    'Demo: Learn FastAPI',
    'Build and test a backend endpoint',
    25,
    'scheduled'
WHERE NOT EXISTS (
    SELECT 1 FROM sessions WHERE title = 'Demo: Learn FastAPI'
);

INSERT INTO sessions (title, goal, scheduled_duration, status)
SELECT
    'Demo: Practice Python testing',
    'Write tests for valid and invalid status transitions',
    30,
    'scheduled'
WHERE NOT EXISTS (
    SELECT 1
    FROM sessions
    WHERE title = 'Demo: Practice Python testing'
);

INSERT INTO sessions (title, goal, scheduled_duration, status)
SELECT
    'Demo: Review React',
    'Practice connecting the frontend to the API',
    20,
    'scheduled'
WHERE NOT EXISTS (
    SELECT 1 FROM sessions WHERE title = 'Demo: Review React'
);

COMMIT;