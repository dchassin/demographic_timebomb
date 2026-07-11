import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from warnings import warn

class Population:

    adult_age = 18 
    immigrant_ages = list(range(18,45,1))
    senior_age = 65

    def __init__(self,
        country,
        year,
        run_to=None,
        immigration=0.675,
        fertility_change_rate=-0.001):
        """Population constructor

        Arguments:
        - country: country name (abbreviated); used for initial file name, e.g. XY.csv
        - year: initial year; used for initial file name, e.g., XY.csv
        - run_to: run simulation to year
        - immigration: number of adult immigrants per year (in millions/year)    
        - fertility_change_rate: change in fertility rate per person (fractional annual change)
        """        
        self.year = year
        self.immigration = immigration if immigration else 0
        self.fertility_change_rate = fertility_change_rate
        self.country = country.upper()

        data = pd.read_csv(f"{country.lower()}{year}.csv",dtype=np.float64).fillna(0).set_index("age")
        dt = data.index.diff().values[1:]
        assert dt.std() == 0.0, "timestep is not uniform"
        assert dt.mean() == 1.0, "timestep is not unitary"
        assert min(data.index) == 0.0, "age 0 not found"

        self.data = self.sync(data,year)
        
        if run_to is not None and run_to > year:
            self.run_to(run_to) 

    def dataframe(self):
        
        return self.data
        
    def print(self,**kwargs):
        
        print(self.data,**kwargs)

    def to_csv(self,*args,**kwargs):
        
        return self.data.to_csv(*args,**kwargs)

    def sync(self,data,year=None,update=False):

        if update:

            data["male_change[pu]"] = 1 / data["males[M]"]
            data["female_change[pu]"] = 1 / data["females[M]"]

            male_births = [round((data["male_births[M/y]"].sum() - data.loc[0,"male_deaths[M/y]"]),6)]
            female_births = [round((data["female_births[M/y]"].sum() - data.loc[0,"female_deaths[M/y]"]),6)]
            
            male_aging = round(data["males[M]"] - data["male_deaths[M/y]"],6).clip(lower=0).values.tolist()
            female_aging =  round(data["females[M]"] - data["female_deaths[M/y]"],6).clip(lower=0).values.tolist()

            male_immigrants = round(data["immigrants[M/y]"] / 2,6).values
            female_immigrants = round(data["immigrants[M/y]"] / 2,6).values

            data["males[M]"] = np.array(male_births+male_aging[:-1])+male_immigrants
            data["females[M]"] = np.array(female_births+female_aging[:-1])+female_immigrants

            data["male_change[pu]"] = round(data["male_change[pu]"] * (1 + data["males[M]"]),3)
            data["female_change[pu]"] = round(data["female_change[pu]"] * (1 + data["females[M]"]),3)

        data["birth_rate[/y]"] *= self.fertility_change_rate + 1
        data["births[M/y]"] = round(data["females[M]"] * data["birth_rate[/y]"],6)
        data["male_births[M/y]"] = round(data["births[M/y]"] * data["birth_ratio"]/(data["birth_ratio"]+1),3)
        data["female_births[M/y]"] = round(data["births[M/y]"] / (data["birth_ratio"]+1),3)

        data["male_deaths[M/y]"] = round(data["males[M]"] * data["male_deathrate[/y]"],6)
        data["female_deaths[M/y]"] = round(data["females[M]"] * data["female_deathrate[/y]"],6)

        data["immigrants[M/y]"] = 0.0
        data.loc[self.immigrant_ages,"immigrants[M/y]"] = round(self.immigration / len(self.immigrant_ages),6)

        if not year is None:
            data["year"] = year

        return data

    def run_to(self,year):
        result = [self.data]
        for t in range(self.year+1,year):
            self.data = self.sync(result[-1].copy(),year,True)
            self.data.year = t
            result.append(self.data)

        self.data = pd.concat(result).reset_index().set_index(["year","age"]).sort_index()

    def population(self,adult_age=None,senior_age=None):
        
        if adult_age is None:
            adult_age = self.adult_age
        if senior_age is None:
            senior_age = self.senior_age
        
        return pd.DataFrame({
            "Children":(self.data.loc[np.s_[:,:adult_age],["males[M]","females[M]"]].groupby("year").sum()).sum(axis=1),
            "Adults":(self.data.loc[np.s_[:,adult_age:senior_age],["males[M]","females[M]"]].groupby("year").sum()).sum(axis=1),
            "Seniors":(self.data.loc[np.s_[:,senior_age:],["males[M]","females[M]"]].groupby("year").sum()).sum(axis=1),
            })

    def plot_population(self,**kwargs):

        population = self.population()

        return population.sum(axis=1),population.plot.area(**kwargs)

    def plot_dependents(self,**kwargs):

        population = self.population()
        population = pd.DataFrame({"Dependents":(population["Children"]+population["Seniors"]) / population["Adults"]})
    
        return population.sum(axis=1),population.plot(**kwargs)

if __name__ == "__main__":

    pd.options.display.max_columns = None
    pd.options.display.width = None
    pd.options.display.max_rows = None

    test = Population("usa",2020,2100,immigration=1.0,fertility_change_rate=-0.001)
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
    print(pop)
    
    plt.clf()
    pop,fig2 = test.plot_dependents(
        title=test.country,
        grid=True,
        xlabel="Year",
        ylabel="Dependents per adult",
        legend = False
        )
    fig2.figure.savefig("dependents.png")
