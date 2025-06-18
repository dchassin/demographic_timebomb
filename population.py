import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Population:

    # children are ages 0-20
    adult_age = 25 # adults are ages 25-65
    immigrant_age = 45 # immigrants age 25-45
    senior_age = 70 # seniors are ages 70-105

    def __init__(self,country,year,run_to=None,immigration=0.675,fertility_change_rate=-0.001):
        """Population constructor

        Arguments:
        - country: country name (abbreviated); used for initial file name, e.g. XY.csv
        - year: initial year; used for initial file name, e.g., XY.csv
        - run_to: run simulation to year
        - immigration: number of adult immigrants per year (in millions/year)    
        - fertility_change_rate: change in fertility rate per person (fractional annual change)
        """        
        self.year = year
        self.country = country.upper()
        self.data = pd.read_csv(f"{country.lower()}{year}.csv",index_col="Age").fillna(0)
        self.data["Year"] = year
        self.immigration = immigration*1e6 if immigration else 0
        self.fertility_change_rate = fertility_change_rate
        if run_to is not None and run_to > year:
            self.run_to(run_to) 

    def dataframe(self):
        
        return self.data
        
    def print(self,**kwargs):
        
        print(self.data,**kwargs)

    def to_csv(self,*args,**kwargs):
        
        return self.data.to_csv(*args,**kwargs)

    def __getitem__(self,*args):
        
        return self.data.loc[*args[0]]

    def run_to(self,year):
        result = [self.data]
        for year in range(self.year+1,year+1):
            data = result[-1].copy()
            data["Year"] = year

            adult_male = data.loc[self.adult_age:self.senior_age-5]["Male"].sum()
            adult_female = data.loc[self.adult_age:self.senior_age-5]["Female"].sum()
            adult_total = adult_male + adult_female
            male_fraction = adult_male / adult_total
            female_fraction = adult_female / adult_total
            age_groups = ( self.immigrant_age - self.adult_age ) / 5

            data["Male"] = data["Male+1y"]
            data["Female"] = data["Female+1y"]

            data["Fertility Rate"] = data["Fertility Rate"]*(1+self.fertility_change_rate)**5

            data.loc[self.adult_age:self.immigrant_age,"Male"] += round(male_fraction * self.immigration * 5 / age_groups)
            data.loc[self.adult_age:self.immigrant_age,"Female"] += round(female_fraction * self.immigration * 5 / age_groups)

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

            result.append(data)

        self.data = pd.concat(result).reset_index().set_index(["Year","Age"])

    def population(self,adult_age=None,senior_age=None):
        
        if adult_age is None:
            adult_age = self.adult_age
        if senior_age is None:
            senior_age = self.senior_age
        
        return pd.DataFrame({
            "Children":(self.data.loc[np.s_[:,:adult_age-5],["Male","Female"]].groupby("Year").sum()).sum(axis=1),
            "Adults":(self.data.loc[np.s_[:,adult_age:senior_age-5],["Male","Female"]].groupby("Year").sum()).sum(axis=1),
            "Seniors":(self.data.loc[np.s_[:,senior_age:],["Male","Female"]].groupby("Year").sum()).sum(axis=1),
            })

    def plot_population(self,**kwargs):

        population = self.population()/1e6

        return population.sum(axis=1),population.plot.area(**kwargs)

    def plot_dependents(self,**kwargs):

        population = self.population()/1e6
        population = pd.DataFrame({"Dependents":(population["Children"]+population["Seniors"]) / population["Adults"]})
    
        return population.sum(axis=1),population.plot(**kwargs)

if __name__ == "__main__":

    test = Population("usa",2020,2100)
    test.to_csv("population.csv")

    plt.clf()
    pop,fig1 = test.plot_population(
        title=test.country,
        grid=True,
        xlabel="Year",
        ylabel="Population (M)",
        legend=True,
        )
    plt.savefig("population.png")
    
    plt.clf()
    pop,fig2 = test.plot_dependents(
        title=test.country,
        grid=True,
        xlabel="Year",
        ylabel="Dependents per adult",
        legend = False
        )
    fig2.figure.savefig("dependents.png")
