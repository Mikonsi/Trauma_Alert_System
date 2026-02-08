-- TODO: This will run on first initialization, use it to prepoplate tables in db
CREATE TABLE IF NOT EXISTS staff (
    moh_id INT PRIMARY KEY,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL   
)

CREATE TABLE IF NOT EXISTS calls(
    call_id BIGINT PRIMARY KEY,
    patient VARCHAR(80),
    date_of_call DATETIME NOT NULL,
    date_of_birth DATE 
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
)

CREATE TABLE IF NOT EXISTS staff_quarantine (
    moh_id INT PRIMARY KEY,
    last_name VARCHAR(50),
    first_name VARCHAR(50),
    level VARCHAR(20) 
)

CREATE TABLE IF NOT EXISTS calls_quarantine(
    call_id BIGINT PRIMARY KEY,
    patient VARCHAR(80),
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
    paramedic_3_id INT,
);


-- CREATE VIEW



-- This is the python search table from my Google Colab

-- target_medic = input("Enter Medic First or Last Name: ")
-- db.sql(
--     f'''
--     SELECT Name, COUNT(DISTINCT "Call Number/Patient Number") AS Total_Calls,
--     SUM("CTAS 1-Resus") AS Total_CTAS1, SUM(Ped_CTAS1) AS Ped_CTAS1,
--     SUM("CTAS 2-Emerg") AS Total_CTAS2, SUM(Ped_CTAS2) AS Ped_CTAS2,
--     SUM(CASE WHEN Deceased == 'BHP TOR' THEN 1 ELSE 0 END) AS Num_TORs,
--     SUM(CASE WHEN Deceased == 'Obviously Dead' THEN 1 ELSE 0 END) AS Num_Code5s,
--     CallDate_Year AS Year
--     FROM acuity_df
--     WHERE Name LIKE '%{target_medic}%'
--     GROUP BY Name, Year
--     HAVING Total_Calls > 10
--     ORDER BY Year DESC, Total_Calls ASC, Total_CTAS1 DESC
--    '''
-- )
