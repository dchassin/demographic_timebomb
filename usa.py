import os
import sys
import pandas as pd

pd.options.display.max_columns = None
pd.options.display.width = None
pd.options.display.max_rows = None

data = pd.read_csv("usa2020.csv")
data.age = data.age-4
data.loc[len(data)] = 0
data.loc[len(data)-1,"age"] = 105
data["population"] = data.males + data.females
data["ratio"] = data.males/data.females
data.fillna(0,inplace=True)
data.drop(["males","females"],axis=1,inplace=True)
population = data.population.sum()
data = pd.DataFrame({"age":range(1,106,1)}).set_index("age").join(data.set_index("age")).reset_index()
data = data.interpolate("quadratic").clip(lower=0)
data.population = round(data.population*population/data.population.sum())
data.fillna(0,inplace=True)
data.set_index("age",inplace=True)

print(data)