"""Demographic Timebomb"""

import pandas as pd

pd.options.display.max_columns = None
pd.options.display.width = None

country = "usa"
year0 = 2020
yearN = 2100

adult_age=25
senior_age=70

data = pd.read_csv(f"{country}{year0}.csv",index_col="Age").fillna(0)

result = [pd.DataFrame({
    "Year": [year0],
    "Children": [data.loc[:adult_age,"Male"].sum() + data.loc[:adult_age,"Female"].sum()],
    "Adults": [data.loc[adult_age:senior_age,"Male"].sum() + data.loc[adult_age:senior_age,"Female"].sum()],
    "Seniors": [data.loc[senior_age:,"Male"].sum() + data.loc[senior_age:,"Female"].sum()],
    })]

for year in range(year0+1,yearN+1):
    
    data["Male"] = data["Male+1y"]
    data["Female"] = data["Female+1y"]

    data["Male births/y"] = round(data["Female"]*data["Fertility Rate"]*data["MF Birth Ratio"]/2)
    data["Female births/y"] = round(data["Female"]*data["Fertility Rate"]/data["MF Birth Ratio"]/2)

    data["Male deaths/y"] = round(data["Male"]*(data["Male"]+data["Female"])/(data["Male"]+data["Female"]/data["MF Death Ratio"])*data["Deathrate"]/5)
    data["Female deaths/y"] = round(data["Female"]*(data["Male"]+data["Female"])/(data["Male"]*data["MF Death Ratio"]+data["Female"])*data["Deathrate"]/5)
    data.loc[105,"Male deaths/y"] = data.loc[105,"Male"]
    data.loc[105,"Female deaths/y"] = data.loc[105,"Female"]
    
    data.loc[5,"Male+1y"] = round(data.loc[5,"Male"]*0.8 + data["Male births/y"].sum() - data.loc[5,"Male deaths/y"])
    data.loc[5,"Female+1y"] = round(data.loc[5,"Female"]*0.8 + data["Female births/y"].sum() - data.loc[5,"Female deaths/y"])
    for age in data.index[1:-1]:
        data.loc[age,"Male+1y"] = round(data.loc[age,"Male"]*0.8 + data.loc[age-5,"Male"]*0.2 - data.loc[age,"Male deaths/y"])
        data.loc[age,"Female+1y"] = round(data.loc[age,"Female"]*0.8 + data.loc[age-5,"Female"]*0.2 - data.loc[age,"Female deaths/y"])

    result.append(pd.DataFrame({
        "Year": [year],
        "Children": [data.loc[:adult_age,"Male"].sum() + data.loc[:adult_age,"Female"].sum()],
        "Adults": [data.loc[adult_age:senior_age,"Male"].sum() + data.loc[adult_age:senior_age,"Female"].sum()],
        "Seniors": [data.loc[senior_age:,"Male"].sum() + data.loc[senior_age:,"Female"].sum()],
        }))

population = pd.concat(result).set_index("Year")/1e6
print("Population =",population.sum(axis=1),sep="\n",end="\n\n")
population.plot.area(
    title=country.upper(),
    grid=True,
    xlabel="Year",
    ylabel="Population (M)",
    legend=True,
    ).figure.savefig("population.png")

dependents = pd.DataFrame({
    "Children": (population["Children"]/population["Adults"]),
    "Seniors": (population["Seniors"]/population["Adults"]),
    })
print("Dependents =",dependents.sum(axis=1),sep="\n",end="\n\n")
dependents.plot.area(
    title=country.upper(),
    grid=True,
    xlabel="Year",
    ylabel="Dependents per Adult",
    legend=True,
    ).figure.savefig("dependents.png")
