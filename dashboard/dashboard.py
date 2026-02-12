import marimo

__generated_with = "0.19.7"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import plotly.express as px
    from dotenv import load_dotenv
    import os

    # Load environment variables
    load_dotenv()
    return os, pl


@app.cell
def _(os, pl):
    # Build connection string from environment variables
    user = os.getenv("POSTGRES_USER", "admin")
    password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("DB_NAME", "paramedic_db")
    host = "localhost"
    port = "5432"

    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    # Query the view
    df = pl.read_database_uri(
        query="SELECT * FROM public.trauma_score_dashboard",
        uri=connection_string,
        engine="connectorx"
    )

    df
    return (df,)


@app.cell
def _(df):
    df.head()
    return


if __name__ == "__main__":
    app.run()
