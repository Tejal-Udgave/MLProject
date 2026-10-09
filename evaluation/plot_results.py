
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"

df = pd.read_csv(RESULTS_DIR / "evaluation_results.csv")

# Graph 1: Frequent itemsets by minimum support
itemsets = (
    df[["Min_Support", "Frequent_Itemsets"]]
    .drop_duplicates()
    .sort_values("Min_Support")
)

plt.figure(figsize=(8, 5))
plt.plot(
    itemsets["Min_Support"],
    itemsets["Frequent_Itemsets"],
    marker="o"
)
plt.xlabel("Minimum Support")
plt.ylabel("Number of Frequent Itemsets")
plt.title("Effect of Minimum Support on Frequent Itemsets")
plt.gca().yaxis.set_major_formatter(
    StrMethodFormatter("{x:,.0f}")
)
plt.grid(True)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "frequent_itemsets_graph.png", dpi=300)
plt.close()

# Graph 2: Association rules by minimum confidence
plt.figure(figsize=(8, 5))

for support in sorted(df["Min_Support"].unique()):
    subset = df[df["Min_Support"] == support].sort_values(
        "Min_Confidence"
    )
    plt.plot(
        subset["Min_Confidence"],
        subset["Association_Rules"],
        marker="o",
        label=f"Support = {support:.2f}"
    )

plt.xlabel("Minimum Confidence")
plt.ylabel("Number of Association Rules")
plt.title("Effect of Confidence on Association Rules")
plt.gca().yaxis.set_major_formatter(
    StrMethodFormatter("{x:,.0f}")
)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "association_rules_graph.png", dpi=300)
plt.close()

print("Graphs saved successfully in results/:")
print("- frequent_itemsets_graph.png")
print("- association_rules_graph.png")
