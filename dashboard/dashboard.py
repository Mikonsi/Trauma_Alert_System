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
    return mo, os, pl, px


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
def _(df, mo):
    # Interactive table
    mo.ui.table(df)
    return


@app.cell
def _(df, mo):
    mo.ui.data_explorer(df)
    return


@app.cell
def _(df, mo, px):
    _plot = px.bar_polar(df.Category)
    plot = mo.ui.plotly(df)
    mo.ui.pl
    return


app._unparsable_cell(
    r"""
    mo.ui.
    """,
    name="_"
)


@app.cell
def _(df, mo):
    # Summary stats
    mo.md(f"""
    ## Dashboard Summary

    **Total Records:** {len(df)}

    **Categories:** {df['category'].n_unique()}
    """)
    return


if __name__ == "__main__":
    app.run()
