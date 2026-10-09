
import time
import pandas as pd
from apriori import load_transactions, apriori, generate_rules

CSV_PATH = r"C:\Users\Prathmesh\Downloads\preprocessed_cicids2017.csv"
SAMPLE_SIZE = 10000

print("Loading 10,000 transactions...")
transactions = load_transactions(
    CSV_PATH,
    sample_size=SAMPLE_SIZE,
    include_label=False
)

results = []

# Three support thresholds and two confidence thresholds
for support in [0.05, 0.10, 0.20]:
    print(f"\nTesting minimum support = {support}")
    start = time.perf_counter()

    frequent = apriori(transactions, min_support=support)
    mining_time = time.perf_counter() - start

    for confidence in [0.60, 0.80]:
        rules = generate_rules(
            frequent,
            min_confidence=confidence,
            min_lift=1.0
        )

        results.append({
            "Transactions": len(transactions),
            "Min_Support": support,
            "Min_Confidence": confidence,
            "Min_Lift": 1.0,
            "Frequent_Itemsets": len(frequent),
            "Association_Rules": len(rules),
            "Mining_Time_Seconds": round(mining_time, 2)
        })

        print(
            f"Confidence={confidence}: "
            f"{len(frequent)} itemsets, {len(rules)} rules"
        )

df = pd.DataFrame(results)
df.to_csv("evaluation_results.csv", index=False)

print("\nFinal comparison:")
print(df.to_string(index=False))
print("\nSaved to evaluation_results.csv")
