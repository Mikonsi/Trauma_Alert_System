INSERT INTO calls (last_name, first_name, moh_id, level)
SELECT
    last_name,
    first_name,
    moh_id,
    level
FROM staging_staff
ON CONFLICT (moh_id) DO NOTHING;
