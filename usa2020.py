"""Update US 2020 population data file from usa2020 county and stats files"""
import os
import sys
import pandas as pd
import numpy as np

pd.options.display.max_columns = None
pd.options.display.width = None
# pd.options.display.max_rows = None

RELOAD = False

if not os.path.exists("usa2020.csv") or RELOAD:

    print("Reading raw data",end="...",flush=True)
    data = pd.read_csv("usa2020_county.csv.gz",usecols=["AGE","SEX","RESPOP"],index_col=["AGE","SEX"])
    print("ok")

    print("Processing data",end="...",flush=True)
    data = data.groupby(["AGE","SEX"]).sum()

    # unstack male/female data
    data = data.unstack("SEX")/2 # respop is double counted for some reason
    data.columns=["males[M]","females[M]"]
    data.index.name = "age"

    # interpolate/extrapolate data
    last = data.index[-1]
    data = pd.DataFrame({"age":range(0,110)}).join(data).set_index("age")
    data.loc[110] = [0,0]
    data = data.interpolate("linear")
    data.loc[last:] *= data.loc[last] / data.loc[last:].sum()

    stats = pd.read_csv("usa2020_stats.csv",
        index_col="age",
        converters={"age":lambda x:int(x)-5},
        usecols=["age","birth_rate[/y]","birth_ratio","death_rate[/y]","death_ratio"],
        )
    data = (data/1e6).join(stats)

    # fix death data
    data.loc[109,"death_rate[/y]"] = 1
    data.loc[110] = [0]*len(data.columns)
    data.loc[110,"death_ratio"]= 1
    last = stats.dropna().index[-1]
    for age in range(last+1,109):
        data.loc[age] = [float('nan')]*len(data.columns)
    data.sort_index(inplace=True)

    # interpolate missing data
    data.loc[9,["birth_rate[/y]","birth_ratio"]] = [0,0] # block interpolation before 9
    data = data.interpolate("linear").round(6)
    data["male_deathrate[/y]"] = [float('nan')]*len(data)
    data["female_deathrate[/y]"] = [float('nan')]*len(data)

    # fix birth data
    implied_births = (data["females[M]"] * data["birth_rate[/y]"]).sum() 
    actual_births = data.loc[0,"males[M]"] + data.loc[0,"females[M]"]
    data.loc[:,"birth_rate[/y]"] = round( data.loc[:,"birth_rate[/y]"] * actual_births / implied_births,6)

    # non-elderly deathrates
    males = data.loc[:last,"males[M]"].values
    females = data.loc[:last,"females[M]"].values
    death_rate = data.loc[:last,"death_rate[/y]"].values
    death_ratio = data.loc[:last,"death_ratio"].values
    female_deathrate = death_rate * [(males+females)/(death_ratio*males+females)]
    male_deathrate = female_deathrate * death_ratio
    data.loc[:last,"male_deathrate[/y]"] = male_deathrate.flatten()
    data.loc[:last,"female_deathrate[/y]"] = female_deathrate.flatten()
    data.loc[:last,"deaths[M]"] = round((data.loc[:last,"males[M]"]+data.loc[:last,"females[M]"]) * data.loc[:last,"death_rate[/y]"],6)
    data.loc[:last,"male_deaths[M]"] = round(data.loc[:last,"males[M]"] * data.loc[:last,"male_deathrate[/y]"],6)
    data.loc[:last,"female_deaths[M]"] = round(data.loc[:last,"females[M]"] * data.loc[:last,"female_deathrate[/y]"],6)

    # elderly deathrates
    males = data.loc[last:,"males[M]"].values
    females = data.loc[last:,"females[M]"].values
    data.loc[last:109,"male_deathrate[/y]"] = 1 - males[1:]/males[:-1]
    data.loc[last:109,"female_deathrate[/y]"] = 1 - females[1:]/females[:-1]
    data.loc[last+1:110,"male_deaths[M]"] = data.loc[last+1:110,"males[M]"] * data.loc[last+1:110,"male_deathrate[/y]"]
    data.loc[last+1:110,"female_deaths[M]"] = data.loc[last+1:110,"females[M]"] * data.loc[last+1:110,"female_deathrate[/y]"]
    data.loc[last+1:110,"deaths[M]"] = data.loc[last+1:110,"male_deaths[M]"] + data.loc[last+1:110,"female_deaths[M]"]
    data.loc[last+1:110,"death_ratio"] = data.loc[last+1:110,"male_deaths[M]"] / data.loc[last+1:110,"female_deaths[M]"]

    # cleanup death data
    data.drop(110,axis=0,inplace=True)
    data.drop(["death_rate[/y]","death_ratio","deaths[M]","male_deaths[M]","female_deaths[M]"],inplace=True,axis=1)

    # save to file
    data.round(6).to_csv("usa2020.csv",index=True,header=True)

    print("ok")
else:
    data = pd.read_csv("usa2020.csv",index_col=["age"])

print((data["males[M]"]+data["females[M]"]).sum())
# print((data["females[M]"] * data["birth_rate[/y]"]).sum() - (data.loc[0,"males[M]"] + data.loc[0,"females[M]"]) )
