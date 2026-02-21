import polars as pl
import os
import pathlib 
from dotenv import load_dotenv



load_dotenv(".env")

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("PORT", "5432")
db = os.getenv("DB_NAME")

uri = f"postgresql://{user}:{password}@{host}:{port}/{db}"


CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent
DATA_DIR = PROJECT_ROOT #/  "data_generator"
SQL_DIR = PROJECT_ROOT/ "sql"



def update_staff():
    """This function will read most recent staff csv file from DATA_DIR and will first stage it, check the db for duplicates, then insert into db"""
    
    staff_schema = {
        "last_name": pl.String,
        "first_name": pl.String,
        "moh_id": pl.Int32,
        "level": pl.String,
        "station": pl.Int32,
        "platoon": pl.Int32
    }

    staff_path = DATA_DIR / "staff_list.csv"
    staff_df = pl.read_csv(staff_path)
    
    staff_clean = staff_df.with_columns([
                                            pl.col(col).cast(dtype, strict=False) for col, dtype in staff_schema.items()
                                        ])
    staff_quarantine = staff_clean.filter(
        pl.any_horizontal(
            (pl.col(col).is_not_null()) & (staff_clean[col].is_null())
            for col in staff_schema.keys()
        )
    )
    staff_to_db = staff_clean.join(staff_quarantine, on=staff_df.columns, how="anti")
    staff_to_db.write_database("staff", uri, if_table_exists="append")
    staff_quarantine.write_database("staff_quarantine", uri, if_table_exists="append", engine="sqlalchemy")
    

def update_calls():  
    call_schema = {
        "call_id":pl.Int64,
        "patient": pl.String,
        "date_of_birth": pl.Date,
        "date_of_call": pl.Datetime,
        "problem_code": pl.Float32,
        "ctas": pl.Int32,
        "station": pl.Int32,
        "hospital_type": pl.String,
        "attending_paramedic_id": pl.Int32,
        "paramedic_2_id": pl.Int32,
        "paramedic_3_id": pl.Int32,
    }

    calls_path = DATA_DIR / "call_list.csv"
    calls_df = pl.read_csv(calls_path)
    calls_clean = calls_df.with_columns([
                                            pl.col(col).cast(dtype, strict=False) for col, dtype in call_schema.items()
                                        ])
    quarantine_df = calls_clean.filter(
        pl.any_horizontal(
            (pl.col(col).is_not_null()) & (calls_clean[col].is_null())
        for col in call_schema.keys()
        )
    )
    calls_to_db = calls_clean.join(quarantine_df, on=calls_df.columns, how="anti")
    calls_to_db.write_database("calls", uri, if_table_exists="append", engine="sqlalchemy")
    quarantine_df.write_database("calls_quarantine", uri, if_table_exists="append", engine="sqlalchemy")

def main():
    update_staff()
    update_calls()


main()
