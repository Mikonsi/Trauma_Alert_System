-- TODO: This will run on first initialization, use it to prepopulate tables in db
CREATE TABLE IF NOT EXISTS staff (
    moh_id INT PRIMARY KEY,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL,
    station INT,
    platoon INT   
);

CREATE TABLE IF NOT EXISTS calls(
    call_id BIGINT PRIMARY KEY,
    patient VARCHAR(80),
    date_of_call TIMESTAMP NOT NULL,
    date_of_birth DATE, 
    problem_code FLOAT NOT NULL,
    ctas INT NOT NULL,
    station INT,
    hospital_type VARCHAR(16),
    attending_paramedic_id INT NOT NULL,
    paramedic_2_id INT,
    paramedic_3_id INT,

    CONSTRAINT fk_attending_staff
        FOREIGN KEY(attending_paramedic_id)
        REFERENCES staff(moh_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_paramedic_2
        FOREIGN KEY(paramedic_2_id)
        REFERENCES staff(moh_id)
        ON DELETE RESTRICT,
        
    CONSTRAINT fk_paramedic_3
        FOREIGN KEY(paramedic_3_id)
        REFERENCES staff(moh_id)
        ON DELETE RESTRICT
    
);

CREATE TABLE IF NOT EXISTS staff_quarantine (
    moh_id INT PRIMARY KEY,
    last_name VARCHAR(50),
    first_name VARCHAR(50),
    level VARCHAR(20),
    station INT,
    platoon INT 
);

CREATE TABLE IF NOT EXISTS calls_quarantine(
    call_id BIGINT PRIMARY KEY,
    patient VARCHAR(80),
    date_of_birth DATE,
    date_of_call TIMESTAMP,
    problem_code FLOAT,
    ctas INT NOT NULL,
    station INT,
    hospital_type VARCHAR(16),
    attending_paramedic_id INT,
    paramedic_2_id INT,
    paramedic_3_id INT
);

-- CREATE VIEW
-- Materialized view maybe used here since data is CSV dump, no risk of data becoming stale. Remove Materialized if data source becomes a data stream
-- * Also must add "REFRESH MATERIALIZED VIEW on automation script if materialization is used

-- DROP VIEW IF EXISTS public.trauma_score_dashboard;
CREATE OR REPLACE VIEW public.monthly_exposures AS

WITH patient_ages AS (
    SELECT *, EXTRACT(YEAR FROM AGE(date_of_birth)) AS patient_age
    FROM calls 
),
base_data AS (
    SELECT pa.attending_paramedic_id AS medic_id,
    staff.last_name, staff.first_name,
    pa.call_id, pa.patient_age, pa.ctas, pa.problem_code, pa.hospital_type, pa.date_of_call
    FROM patient_ages pa 
    JOIN staff on pa.attending_paramedic_id = staff.moh_id
    UNION ALL 
    SELECT pa.paramedic_2_id as medic_id,
    staff.last_name, staff.first_name,
    pa.call_id, pa.patient_age, pa.ctas, pa.problem_code, pa.hospital_type, pa.date_of_call
    FROM patient_ages pa 
    JOIN staff ON pa.paramedic_2_id = staff.moh_id
),

traumatic_criteria AS(
    -- Pediatric VSA:
	SELECT medic_id, last_name, first_name, call_id, date_of_call, 'Ped VSA'::text AS Category
	FROM base_data
    WHERE patient_age < 18 AND problem_code IN (1,2)

    UNION ALL

    -- Traumatic VSA (any age)
	SELECT medic_id, last_name, first_name, call_id, date_of_call, 'Traumatic VSA'::text AS Category
	FROM base_data
    WHERE problem_code = 1
    
    UNION ALL

    -- Trauma requiring hospital by-pass
    SELECT medic_id, last_name, first_name, call_id, date_of_call, 'Trauma By-pass'::text AS Category
    FROM base_data
    WHERE hospital_type = 'Trauma Center'
             
    UNION ALL

    SELECT medic_id, last_name, first_name, call_id, date_of_call, 'Young Adult VSA'::text AS Category
	FROM base_data
    WHERE patient_age > 18 AND patient_age < 60 
        AND problem_code IN (1,2)
)
SELECT * FROM traumatic_criteria;


CREATE OR REPLACE VIEW public.trauma_score AS
SELECT 
	last_name,
	first_name,
	Category,
    DATE_TRUNC('month', date_of_call) AS call_month,
	COUNT(DISTINCT call_id) AS monthly_exposure_count,
	ROUND(AVG(COUNT(DISTINCT call_id)) OVER(PARTITION BY Category), 1) AS service_wide_avg,
	RANK() OVER(PARTITION BY Category ORDER BY monthly_exposure_count DESC) AS Rank_in_Category 
FROM monthly_exposures
;

-- Grant select privileges to Grafana:
GRANT SELECT ON public.trauma_score TO admin;
GRANT SELECT ON public.monthly_exposures TO admin;
GRANT SELECT ON public.monthly_exposures TO "user";
GRANT SELECT ON public.trauma_score TO "user";
;
