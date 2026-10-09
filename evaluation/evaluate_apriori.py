
import sys
import time
from pathlib import Path

import pandas as pd

# Allow importing apriori.py from the project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from apriori import load_transactions, apriori, generate_rules

CSV_PATH = Path(r"C:\Users\Prathmesh\Downloads\preprocessed_cicids2017.csv")
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

SAMPLE_SIZE = 10000

print("Loading 10,000 transactions...")
transactions = load_transactions(
    str(CSV_PATH),
    sample_size=SAMPLE_SIZE,
    include_label=False
)

results = []

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

output = pd.DataFrame(results)
output_path = RESULTS_DIR / "evaluation_results.csv"
output.to_csv(output_path, index=False)

print("\nFinal comparison:")
print(output.to_string(index=False))
print(f"\nSaved to {output_path}")
