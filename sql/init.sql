-- TODO: This will run on first initialization, use it to prepoplate tables in db
CREATE TABLE IF NOT EXISTS staff (
    moh_id INT PRIMARY KEY,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL   
);

CREATE TABLE IF NOT EXISTS calls(
    call_id BIGINT PRIMARY KEY,
    patient VARCHAR(80),
    date_of_call TIMESTAMP NOT NULL,
    date_of_birth DATE, 
    problem_code FLOAT NOT NULL,
    ctas INT NOT NULL,
    vitals_bp VARCHAR(10),
    vitals_hr VARCHAR(10),
    vitals_temp VARCHAR(10),
    procedure_1 VARCHAR(60),
    procedure_2 VARCHAR(60),
    attending_paramedic_id INT NOT NULL,
    paramedic_2_id INT,
    paramedic_3_id INT,

    CONSTRAINT fk_attending_staff
        FOREIGN KEY(attending_paramedic_id)
        REFERENCES staff(moh_id)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS staff_quarantine (
    moh_id INT PRIMARY KEY,
    last_name VARCHAR(50),
    first_name VARCHAR(50),
    level VARCHAR(20) 
);

CREATE TABLE IF NOT EXISTS calls_quarantine(
    call_id BIGINT PRIMARY KEY,
    patient VARCHAR(80),
    date_of_birth DATE,
    date_of_call TIMESTAMP,
    problem_code FLOAT,
    ctas INT NOT NULL,
    vitals_bp VARCHAR(10),
    vitals_hr VARCHAR(10),
    vitals_temp VARCHAR(10),
    procedure_1 VARCHAR(60),
    procedure_2 VARCHAR(60),
    attending_paramedic_id INT,
    paramedic_2_id INT,
    paramedic_3_id INT
);

-- CREATE VIEW

-- DROP VIEW IF EXISTS public.trauma_score_dashboard;


-- Materialized view maybe used here since data is CSV dump, no risk of data becoming stale. Remove Materialized if data source becomes a data stream
-- * Also must add "REFRESH MATERIALIZED VIEW on automation script if materialization is used

CREATE OR REPLACE VIEW public.trauma_score_dashboard AS

WITH patient_ages AS (
    SELECT *, EXTRACT(YEAR FROM AGE(date_of_birth)) AS patient_age
    FROM calls 
),
base_data AS (
    SELECT pa.attending_paramedic_id AS medic_id,
    staff.last_name, staff.first_name,
    pa.call_id, pa.patient_age, pa.ctas, pa.problem_code
    FROM patient_ages pa 
    JOIN staff on pa.attending_paramedic_id = staff.moh_id
    UNION ALL 
    SELECT pa.paramedic_2_id as medic_id,
    staff.last_name, staff.first_name,
    pa.call_id, pa.patient_age, pa.ctas, pa.problem_code
    FROM patient_ages pa 
    JOIN staff ON pa.paramedic_2_id = staff.moh_id
),

traumatic_criteria AS(
    -- Pediatric VSA:
	SELECT medic_id, last_name, first_name, call_id, 'Ped VSA'::text AS Category
	FROM base_data
    WHERE patient_age < 18 AND problem_code IN (1,2)

    UNION ALL

    -- Traumatic VSA (any age)
	SELECT medic_id, last_name, first_name, call_id, 'Traumatic VSA'::text AS Category
	FROM base_data
    WHERE problem_code = 1
-- Additional data needs to be added to generator to filter for these:

        -- Trauma requiring hospital by-pass
        -- Any Pediatric CTAS 1
        -- Any Pediatric CTAS 2 (tracked seperately from CTAS 1's)
        -- Medical VSA (age 18-60) where paramedics pronounce on scene

    UNION ALL

    SELECT medic_id, last_name, first_name, call_id, 'Young Adult VSA'::text AS Category
	FROM base_data
    WHERE patient_age > 18 AND patient_age < 60 
    AND problem_code IN (1,2)
	-- Any call where patient dies after paramedic contact
),

medic_exposures AS (
    SELECT medic_id, last_name, first_name, Category,
    COUNT(DISTINCT call_id) AS exposure_count
    FROM traumatic_criteria 
    GROUP BY medic_id, last_name, first_name, Category
)

SELECT 
	last_name,
	first_name,
	Category,
	exposure_count,
	ROUND(AVG(exposure_count) OVER(PARTITION BY Category), 1) AS service_wide_avg,
	RANK() OVER(PARTITION BY Category ORDER BY exposure_count DESC) AS Rank_in_Category 
FROM medic_exposures
;

-- Grant select privildges to Grafana:
GRANT SELECT ON ALL VIEWS IN SCHEMA public TO admin;
GRANT SELECT on public.trauma_score_dashboard TO admin;


;
