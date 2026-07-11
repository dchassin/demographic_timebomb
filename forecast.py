from population import Population
import matplotlib.pyplot as plt

result = {}
ax = None
for fr in [-0.01,0.0,0.01]:
    result[fr] = Population(
        "usa",
        2020,2101,
        immigration=1.0,
        fertility_change_rate=fr,
        )
    ax = result[fr].plot_dependents(ax=ax)[1]

plt.title("USA Fertility Rates")
plt.ylabel("Non-workers per Working Adult")
plt.grid()
plt.legend([f"${x*100:+.0f}$ %/y" for x in result])
plt.savefig("forecast.png")