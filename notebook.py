import marimo

__generated_with = "0.13.15"
app = marimo.App(width="full")


@app.cell
def _(mo):
    ui_immigration = mo.ui.slider(
        label="Immigration: [million/year] ",
        value=1.0,
        start=0.0,
        stop=5.0,
        step=0.1,
        debounce=True,
        show_value=True,
    )
    ui_fertility = mo.ui.slider(
        label="Fertility rate change: [%/year]",
        value=0.0,
        start=-1,
        stop=1,
        step=0.01,
        debounce=True,
        show_value=True,
    )
    mo.hstack([ui_immigration, ui_fertility], justify="start")
    return ui_fertility, ui_immigration


@app.cell
def _(Population, ui_fertility, ui_immigration):
    population = Population("usa",2020,2100,immigration=ui_immigration.value,fertility_change_rate=ui_fertility.value/100)
    return (population,)


@app.cell
def _():
    historical = {
        1900:	76.212168,
        1910:	92.228496,
        1920:	106.021537,
        1930:	122.775046,
        1940:	132.164569,
        1950:	150.697361,
        1960:	179.323175,
        1970:	203.392031,
        1980:	226.545805,
        1990:	248.709873,
        2000:	281.421906,
        2010:	308.745538,
        2020:	331.449281,
    }
    return (historical,)


@app.cell
def _(historical, mo, pd, population):
    fig1 = population.plot_population(
        title=population.country,
        grid=True,
        xlabel="Year",
        ylabel="Population (M)",
        legend=True,
    )[1]
    fig1.plot(pd.DataFrame(data=historical.values(),index=historical.keys()),"--k")
    fig2 = population.plot_dependents(
        title=population.country,
        grid=True,
        xlabel="Year",
        ylabel="Dependents per adult",
        legend=False,
    )[1]
    mo.hstack([fig1,fig2])
    return


@app.cell
def _():
    import marimo as mo
    import os
    import sys
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import pyarrow
    from population import Population

    pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.width = None
    return Population, mo, pd


if __name__ == "__main__":
    app.run()
