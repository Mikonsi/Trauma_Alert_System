import marimo

__generated_with = "0.19.7"
app = marimo.App(width="full", layout_file="layouts/dashboard.grid.json")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import duckdb
    import altair as alt
    from dotenv import load_dotenv
    import os
    import re
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    load_dotenv()
    return alt, mo, os, pl, relativedelta


@app.cell
def _(os, pl):
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("DB_NAME")
    host = "localhost"
    port = "5432"

    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    trauma_score = pl.read_database_uri(
        query="SELECT * FROM public.trauma_score",
        uri=connection_string,
        engine="connectorx"
    )

    df_calls = pl.read_database_uri(
        query="SELECT * FROM public.calls",
        uri=connection_string,
        engine="connectorx"
    )
    return df_calls, trauma_score


@app.cell
def _(trauma_score):
    trauma_score.head()
    return


@app.cell
def _(mo, trauma_score):
    _df = mo.sql(
        f"""
        SELECT last_name, 
            first_name, 
            category, 
            SUM(monthly_exposure_count) AS total_exposure_count, 
            rank_in_category, 
            ROUND(service_wide_avg, 1) AS service_avg_for_category
        FROM trauma_score
        GROUP BY category, call_month, last_name, first_name, monthly_exposure_count, rank_in_category, service_wide_avg
        ORDER BY category, total_exposure_count DESC
        """,
        output=False
    )
    return


@app.cell
def _(mo, trauma_score):
    _df = mo.sql(
        f"""
        WITH RankedByCat AS (
            SELECT last_name, 
            first_name, 
            category, 
            SUM(monthly_exposure_count) AS total_exposure_count, 
            DENSE_RANK() OVER (PARTITION BY category ORDER BY SUM(monthly_exposure_count) DESC) AS rank_per_cat,
            FROM trauma_score 
            GROUP BY last_name, first_name, category
        )
        SELECT * 
        FROM RankedByCat 
        WHERE rank_per_cat <= 5 
        ORDER BY category, rank_per_cat
        """
    )
    return


@app.cell
def _():
    # service_total = (
    #     trauma_score
    #     .filter(pl.col("call_month") >= start_date)
    #     .group_by("category")
    #     .agg(pl.col("monthly_exposure_count").sum().alias("rolling_avg"))
    #     .with_columns([
    #         pl.lit("SERVICE").alias("last_name"),
    #         pl.lit("TOTAL").alias("first_name")
    #     ])
    # )
    return


@app.cell
def _():
    # service_avg = (
    #     trauma_score
    #     .filter(pl.col("call_month") >= start_date)
    #     .group_by("category")
    #     .agg(
    #         (pl.col("monthly_exposure_count").sum() / 
    #          pl.col("last_name").n_unique()).alias("rolling_avg")
    #     )
    #     .with_columns([
    #         pl.lit("SERVICE").alias("last_name"),
    #         pl.lit("AVERAGE").alias("first_name")
    #     ])
    # )
    return


@app.cell
def _(mo):
    window_slider = mo.ui.slider(start=1, stop=12, step=1, value=3, label="Rolling Window (Months)")
    window_slider
    return (window_slider,)


@app.cell
def _(mo, pl, trauma_score):
    staff = trauma_score.select(pl.col("last_name") + ", " + pl.col("first_name")).unique().to_series().to_list()
    target_staff = mo.ui.dropdown(staff, label="Select By Staff")
    target_staff
    return (target_staff,)


@app.cell
def _(mo, trauma_score):
    categories = trauma_score["category"].unique().to_list()
    target_category = mo.ui.dropdown(categories, label="Select By Category")
    target_category
    return


@app.cell
def _(pl, relativedelta, target_staff, trauma_score, window_slider):
    latest_date = trauma_score["call_month"].max()
    start_date = latest_date - relativedelta(months=window_slider.value)

    if target_staff.value:
        rolling_top_10 = (
            trauma_score
            .filter((pl.col("call_month") >= start_date) & (pl.col("last_name") + ", " + pl.col("first_name") == target_staff.value))
            .group_by(["category", "last_name", "first_name"])
            .agg(pl.col("monthly_exposure_count").sum().alias("rolling_avg"))
            .sort("rolling_avg", descending=True)
        )
    else:
        rolling_top_10 = (
            trauma_score
            .filter(pl.col("call_month") >= start_date)
            .group_by(["category", "last_name", "first_name"])
            .agg(pl.col("monthly_exposure_count").sum().alias("rolling_avg"))
            .sort("rolling_avg", descending=True)
            .group_by("category")
            .head(10)
            .sort(["category", "rolling_avg"], descending=[False, True])
        )

    # combined_data = pl.concat([
    #     rolling_top_10.select(service_total.columns), 
    #     service_total, 
    #     service_avg
    # ])
    # combined_data

    rolling_top_10
    return latest_date, rolling_top_10, start_date


@app.cell
def _(alt, pl, rolling_top_10, window_slider):
    chart_data = rolling_top_10.with_columns(
        (pl.col("last_name") + ", " + pl.col("first_name")).alias("full_name")
    )

    # 2. Build the chart
    bar_chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            # X-axis: The sum of exposures
            x=alt.X("rolling_avg:Q", title="Total Exposure Count"),

            # Y-axis: Paramedic names, sorted by the exposure count
            y=alt.Y("full_name:N", sort="-x", title="Staff Member"),

            # Color: Group by Category to make the Top 10s distinct
            color=alt.Color("category:N", legend=alt.Legend(title="Medical Category")),

            # Tooltip for interactivity
            tooltip=["full_name", "category", "rolling_avg"]
        )
        .properties(
            title=f"Top Staff Exposure (Last {window_slider.value} Months)",
            width=600,
            height=alt.Step(20) # This keeps bar thickness consistent as the list grows/shrinks
        )
    )

    bar_chart
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    ctas_list = range(1,6)
    ctas_dropdown = mo.ui.dropdown(ctas_list, label="Select CTAS Level", value=ctas_list[0])
    ctas_dropdown
    return (ctas_dropdown,)


@app.cell
def _(alt, ctas_dropdown, df_calls, pl):
    priority_by_station = (
        df_calls
        .filter(pl.col("ctas")==ctas_dropdown.value)
        .group_by("station")
        .agg(pl.count("call_id").alias("call_count"))
        .with_columns(
            (pl.col("call_count")/ pl.col("call_count").sum() * 100).round(1).alias("percentage")
        )
        .sort("station", descending=False)
    )

    pie_chart = (
        alt.Chart(priority_by_station)
        .mark_arc(innerRadius=50) # innerRadius turns a pie into a modern donut chart
        .encode(
            theta=alt.Theta(field="call_count", type="quantitative"),
            color=alt.Color(field="station", type="nominal", scale=alt.Scale(scheme='category10')),
            tooltip=["station", "call_count", "percentage"]
        )
        .properties(
            title=f"Station Breakdown: CTAS {ctas_dropdown.value}",
            width=300,
            height=300
        )
    )

    pie_chart
    return


@app.cell
def _(
    alt,
    latest_date,
    pl,
    relativedelta,
    start_date,
    target_staff,
    trauma_score,
    window_slider,
):
    latest_date_ = trauma_score["call_month"].max()
    start_date_ = latest_date - relativedelta(months=window_slider.value)

    # 1. Prepare base data for the window
    window_data = trauma_score.filter(pl.col("call_month") >= start_date)

    # 2. Calculate TOTAL exposures for EVERY staff member in this window, per category
    staff_totals = (
        window_data
        .group_by(["category", "last_name", "first_name"])
        .agg(pl.col("monthly_exposure_count").sum().alias("total_exposures"))
    )

    # 3. Calculate Service Median from those totals
    service_medians = (
        staff_totals
        .group_by("category")
        .agg(pl.col("total_exposures").median().alias("benchmark_value"))
        .with_columns(pl.lit("Service Median").alias("type"))
    )

    # 4. Get the selected staff's total
    selected_staff_total = (
        staff_totals
        .filter((pl.col("last_name") + ", " + pl.col("first_name")) == target_staff.value)
        .select(["category", "total_exposures"])
        .rename({"total_exposures": "benchmark_value"})
        .with_columns(pl.lit(target_staff.value).alias("type"))
    )

    # 5. Combine for visualization
    viz_data = pl.concat([service_medians, selected_staff_total])

    # Identify unique categories from the data to be dynamic
    unique_categories = sorted(trauma_score["category"].unique().to_list())
    charts = []

    for cat in unique_categories:
        cat_data = viz_data.filter(pl.col("category") == cat)

        # Ensure the selected staff is represented even with 0 exposures
        if cat_data.filter(pl.col("type") == target_staff.value).is_empty():
            cat_data = pl.concat([
                cat_data, 
                pl.DataFrame({
                    "category": [cat],
                    "benchmark_value": [0.0],
                    "type": [target_staff.value]
                })
            ])

        chart = (
            alt.Chart(cat_data)
            .mark_bar()
            .encode(
                x=alt.X("type:N", title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("benchmark_value:Q", title="Total Exposures"),
                color=alt.Color("type:N", legend=None, scale=alt.Scale(domain=[target_staff.value, "Service Median"], range=["#EF553B", "#636EFA"])),
                tooltip=["category", "type", "benchmark_value"]
            )
            .properties(
                title=f"{cat}",
                width=200,
                height=150
            )
        )
        charts.append(chart)

    # Layout the charts in a 2x2 grid if there are 4 categories
    return


if __name__ == "__main__":
    app.run()
