import polars as pl
import os
from dotenv import load_dotenv


load_dotenv("../.env")

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("PORT")
db = os.getenv("DB_NAME")

uri = f"postgresql://{user}:{password}@{host}:{port}/{db}"

def update_staff():
    staff_schema = {
        "last_name": pl.String,
        "first_name": pl.String,
        "moh_id": pl.Int32,
        "level": pl.String
    }
    staff_df = pl.read_csv("../data_generator/staff_list.csv")
    
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
    staff_to_db.write_database("staff", uri, if_table_exists="append", engine="sqlalchemy")
    staff_quarantine.write_database("staff_quarantine", uri, if_table_exists="append", engine="sqlalchemy")
    

def update_calls():  
    call_schema = {
        "call_id":pl.String,
        "patient": pl.String,
        "date_of_call": pl.Datetime,
        "problem_code": pl.Float32,
        "ctas": pl.Int32,
        "vitals_bp": pl.String,
        "vitals_hr": pl.Int32,
        "vitals_temp": pl.Float32,
        "procedure_1": pl.String,
        "procedure_2":pl.String,
        "attending_paramedic_id": pl.String,
        "paramedic_2_id": pl.String,
        "paramedic_3_id": pl.String,
    }
    calls_df = pl.read_csv("../data_generator/call_list.csv")
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
