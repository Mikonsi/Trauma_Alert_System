import marimo

__generated_with = "0.19.7"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import polars as pl 
    import duckdb
    return mo, pl


@app.cell
def _(pl):
    staff = pl.read_csv("staff_list.csv")
    calls = pl.read_csv("call_list.csv", 
                        schema_overrides = {
                           "date_of_birth": pl.Date
                       })
    return calls, staff


@app.cell
def _(calls, staff):
    print(f"Call Cols: {calls.columns}")
    print(f"Staff Cols: {staff.columns}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Potentially Traumatizing Calls
    - Traumatic VSA (any age)
    - Trauma requiring hospital by-pass
    - Pediatric VSA (age < 18)
    - Any Pediatric CTAS 1
    - Any Pediatric CTAS 2 (tracked seperately from CTAS 1's)
    - Medical VSA (age 18-60) where paramedics pronounce on scene
    - Any call where patient dies after paramedic contact
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Important Views:
    - Each type of traumatic call summed by Paramedic, and relative to service mean/median/mode paramedics
    - Aggregate total exposure to all possibly traumatizing calls to each paramedic and relative to service mean/median/mode
    """)
    return


@app.cell
def _(calls, mo, staff):
    _df = mo.sql(
        f"""
        WITH patient_ages AS (
            SELECT *, 
              EXTRACT(YEAR FROM AGE(date_of_birth)) AS patient_age
        	FROM calls
        )

        SELECT call_id, date_of_call, ctas, problem_code, patient_age, attending_paramedic_id, paramedic_2_id,
            staff_1.last_name AS attending_last_name,
            staff_1.first_name AS attending_first_name,
            staff_2.last_name AS paramedic_2_last_name,
            staff_2.first_name AS paramedic_2_first_name
            FROM patient_ages
            LEFT JOIN staff staff_1 ON patient_ages.attending_paramedic_id = staff_1.moh_id
            LEFT JOIN staff staff_2 ON patient_ages.paramedic_2_id = staff_2.moh_id
        WHERE patient_age < 18
        	AND ctas < 3
        """
    )
    return


@app.cell
def _(calls, mo, staff):
    _df = mo.sql(
        f"""
        WITH patient_ages AS (
            SELECT *, 
              EXTRACT(YEAR FROM AGE(date_of_birth)) AS patient_age
        	FROM calls
        ),

        total_ped_exposures AS (
            SELECT pa.attending_paramedic_id AS medic_id, staff.last_name, staff.first_name, call_id
            FROM patient_ages as pa
            JOIN staff ON pa.attending_paramedic_id = staff.moh_id
            UNION 
            SELECT pa.paramedic_2_id AS medic_id, last_name, first_name, call_id 
            FROM patient_ages as pa
            JOIN staff ON pa.paramedic_2_id = staff.moh_id
            WHERE patient_age < 18
        	AND ctas < 3
        ),

        medic_exposures AS (
            SELECT medic_id, COUNT(DISTINCT call_id) AS total_acute_ped, last_name, first_name
            FROM total_ped_exposures
            GROUP BY medic_id, last_name, first_name
        )

        SELECT total_acute_ped, last_name, first_name
        FROM medic_exposures AS me
        GROUP BY last_name, first_name, total_acute_ped
        ORDER BY total_acute_ped DESC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Pediatric VSA:
    """)
    return


@app.cell
def _(calls, mo, staff):
    _df = mo.sql(
        f"""
        WITH patient_ages AS (
            SELECT *, 
              EXTRACT(YEAR FROM AGE(date_of_birth)) AS patient_age
        	FROM calls
        ),

        total_ped_exposures AS (
            SELECT pa.attending_paramedic_id AS medic_id, staff.last_name, staff.first_name, call_id, problem_code
            FROM patient_ages as pa
            JOIN staff ON pa.attending_paramedic_id = staff.moh_id
            UNION 
            SELECT pa.paramedic_2_id AS medic_id, last_name, first_name, call_id, problem_code 
            FROM patient_ages as pa
            JOIN staff ON pa.paramedic_2_id = staff.moh_id
            WHERE patient_age < 18
        		AND ctas < 3
        ),

        medic_exposures AS (
            SELECT medic_id, COUNT(DISTINCT call_id) AS total_acute_ped, last_name, first_name
            FROM total_ped_exposures
            WHERE problem_code = 1
            	OR problem_code = 2
            GROUP BY medic_id, last_name, first_name
        )

        SELECT total_acute_ped, last_name, first_name,
        FROM medic_exposures AS me
        GROUP BY last_name, first_name, total_acute_ped
        ORDER BY total_acute_ped DESC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Repeating the same logic for all "Potentially Traumatizing Calls"
    """)
    return


@app.cell
def _(calls, mo, staff):
    _df = mo.sql(
        f"""
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
            -- Trauma requiring hospital by-pass
        	-- Any Pediatric CTAS 1
        	-- Any Pediatric CTAS 2 (tracked seperately from CTAS 1's)
        	-- Medical VSA (age 18-60) where paramedics pronounce on scene

            UNION ALL

            SELECT medic_id, last_name, first_name, call_id, 'Young VSA'::text AS Category
        	FROM base_data
            WHERE patient_age > 18 AND patient_age < 60 
            AND problem_code = 1 OR problem_code = 2
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
        """
    )
    return


@app.cell
def _(calls, mo):
    _df = mo.sql(
        f"""
        SELECT * FROM calls
        """
    )
    return


@app.cell
def _(calls, mo, staff):
    _df = mo.sql(
        f"""
        -- CREATE OR REPLACE VIEW monthly_exposures AS
            WITH patient_ages AS (
                -- Cast date_of_call here to ensure it's a date type
                SELECT *, 
                       EXTRACT(YEAR FROM AGE(date_of_birth)) AS patient_age,
                       date_of_call::DATE AS call_date -- Cast to DATE
                FROM calls 
            ),
            base_data AS (
                SELECT pa.attending_paramedic_id AS medic_id,
                staff.last_name, staff.first_name,
                pa.call_id, pa.patient_age, pa.ctas, pa.problem_code, pa.hospital_type, pa.call_date
                FROM patient_ages pa 
                JOIN staff on pa.attending_paramedic_id = staff.moh_id
                UNION ALL 
                SELECT pa.paramedic_2_id as medic_id,
                staff.last_name, staff.first_name,
                pa.call_id, pa.patient_age, pa.ctas, pa.problem_code, pa.hospital_type, pa.call_date
                FROM patient_ages pa 
                JOIN staff ON pa.paramedic_2_id = staff.moh_id
            	UNION ALL
            	SELECT pa.paramedic_3_id as medic_id,
                staff.last_name, staff.first_name,
                pa.call_id, pa.patient_age, pa.ctas, pa.problem_code, pa.hospital_type, pa.call_date
                FROM patient_ages pa 
                JOIN staff ON pa.paramedic_3_id = staff.moh_id

            ),

            traumatic_criteria AS(
                -- Pediatric VSA:
            	SELECT medic_id, last_name, first_name, call_id, call_date, 'Ped VSA'::text AS Category
            	FROM base_data
                WHERE patient_age < 18 AND problem_code IN (1,2)

                UNION ALL

                -- Traumatic VSA (any age)
            	SELECT medic_id, last_name, first_name, call_id, call_date, 'Traumatic VSA'::text AS Category
            	FROM base_data
                WHERE problem_code = 1

                UNION ALL

                -- Trauma requiring hospital by-pass
                SELECT medic_id, last_name, first_name, call_id, call_date, 'Trauma By-pass'::text AS Category
                FROM base_data
                WHERE hospital_type = 'Trauma Center'

                UNION ALL

                SELECT medic_id, last_name, first_name, call_id, call_date, 'Young Adult VSA'::text AS Category
            	FROM base_data
                WHERE patient_age > 18 AND patient_age < 60 
                    AND problem_code IN (1,2)
            )
            SELECT * FROM traumatic_criteria;
        """
    )
    return


if __name__ == "__main__":
    app.run()
