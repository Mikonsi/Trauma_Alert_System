import marimo

__generated_with = "0.19.7"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    return


@app.cell
def _():
    import os
    import dotenv
    import polars as pl
    from sqlalchemy import create_engine



    # engine = sqlalchemy.create_engine(sqlalchemy)
    return create_engine, os


@app.cell
def _(create_engine, os):
    load_dotenv = (".env")

    _password = os.environ.get("POSTGRES_PASSWORD")
    _username = os.environ.get("POSTGRES_USER")
    _host = os.environ.get("POSTGRES_HOST")
    _port=os.environ.get("PORT")
    _database = os.environ.get("DB_NAME")
    DATABASE_URL = f"postgresql://{_username}:{_password}@{_host}:{_port}/{_database}"

    uri = f"postgresql://{_username}:{_password}@{_host}:{_port}/{_database}"

    engine = create_engine(uri)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
