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
    import sqlmodel

    _password = os.environ.get("POSTGRES_PASSWORD")
    _username = os.environ.get("POSTGRES_USER")
    _host = os.environ.get("POSTGRES_HOST")
    _database = os.environ.get("DB_NAME")
    DATABASE_URL = f"postgresql://{_username}:{_password}@{_host}:5432/{_database}"
    engine = sqlmodel.create_engine(DATABASE_URL)
    return


if __name__ == "__main__":
    app.run()
