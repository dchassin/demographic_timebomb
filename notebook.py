import marimo

__generated_with = "0.13.15"
app = marimo.App(width="full")


@app.cell
def _(Population, ui_fertility, ui_immigration):
    population = Population("usa",2020,2100,immigration=ui_immigration.value,fertility_change_rate=ui_fertility.value/100)
    return (population,)


@app.cell
def _(mo):
    ui_immigration = mo.ui.slider(
        label="Immigration: [million/year] ",
        value=0.675,
        start=0.0,
        stop=5.0,
        step=0.005,
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
def _(mo, population):
    mo.hstack(
        [
            population.plot_population(
                title=population.country,
                grid=True,
                xlabel="Year",
                ylabel="Population (M)",
                legend=True,
            )[1],
            population.plot_dependents(
                title=population.country,
                grid=True,
                xlabel="Year",
                ylabel="Dependents per adult",
                legend=False,
            )[1],
        ]
    )
    return


@app.cell
def _(population):
    population.dataframe()[["Male","Female","Fertility Rate"]].groupby("Year").sum()
    return


@app.cell
def _():
    import marimo as mo
    import os
    import sys
    import pandas as pd
    import matplotlib.pyplot as plt
    import pyarrow
    from population import Population

    pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.width = None
    return Population, mo


if __name__ == "__main__":
    app.run()
