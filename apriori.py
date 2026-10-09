
from itertools import combinations
from collections import Counter
import argparse
import pandas as pd


def load_transactions(csv_path, sample_size=None, include_label=False):
    """Load the preprocessed CSV and convert each row into a transaction."""
    df = pd.read_csv(csv_path, nrows=sample_size)

    if "Label" in df.columns and not include_label:
        df = df.drop(columns=["Label"])

    df = df.dropna()

    transactions = [
        frozenset(str(value) for value in row if pd.notna(value))
        for row in df.itertuples(index=False, name=None)
    ]

    print(f"Transactions loaded: {len(transactions)}")
    print(f"Columns used: {list(df.columns)}")
    return transactions


def generate_candidates(previous_frequent, k):
    """Generate k-item candidates using the Apriori join step."""
    previous_frequent = set(previous_frequent)
    previous_list = sorted(previous_frequent, key=lambda itemset: tuple(sorted(itemset)))
    candidates = set()

    for i in range(len(previous_list)):
        for j in range(i + 1, len(previous_list)):
            left = previous_list[i]
            right = previous_list[j]

            joined = left | right
            if len(joined) != k:
                continue

            if all(
                frozenset(subset) in previous_frequent
                for subset in combinations(sorted(joined), k - 1)
            ):
                candidates.add(joined)

    return candidates


def apriori(transactions, min_support=0.05):
    """Return frequent itemsets and their support values."""
    if not transactions:
        raise ValueError("The transaction dataset is empty.")

    if not 0 < min_support <= 1:
        raise ValueError("Minimum support must be in (0, 1].")

    total_transactions = len(transactions)
    item_counts = Counter()

    for transaction in transactions:
        item_counts.update(transaction)

    current = {
        frozenset([item]): count / total_transactions
        for item, count in item_counts.items()
        if count / total_transactions >= min_support
    }

    frequent = dict(current)
    k = 2

    while current:
        candidates = generate_candidates(current.keys(), k)
        if not candidates:
            break

        candidate_counts = Counter()
        for transaction in transactions:
            for candidate in candidates:
                if candidate.issubset(transaction):
                    candidate_counts[candidate] += 1

        next_frequent = {
            candidate: count / total_transactions
            for candidate, count in candidate_counts.items()
            if count / total_transactions >= min_support
        }

        print(f"k={k}: {len(next_frequent)} frequent itemsets")

        if not next_frequent:
            break

        frequent.update(next_frequent)
        current = next_frequent
        k += 1

    return frequent


def generate_rules(frequent_itemsets, min_confidence=0.60, min_lift=1.0):
    """Generate association rules with support, confidence and lift."""
    rules = []

    for itemset, support_xy in frequent_itemsets.items():
        if len(itemset) < 2:
            continue

        items = sorted(itemset)
        for subset_size in range(1, len(items)):
            for antecedent_items in combinations(items, subset_size):
                antecedent = frozenset(antecedent_items)
                consequent = itemset - antecedent

                if not consequent:
                    continue

                support_x = frequent_itemsets.get(antecedent)
                support_y = frequent_itemsets.get(consequent)

                if support_x is None or support_y is None:
                    continue

                confidence = support_xy / support_x
                lift = confidence / support_y

                if confidence >= min_confidence and lift >= min_lift:
                    rules.append({
                        "Antecedent": ", ".join(sorted(antecedent)),
                        "Consequent": ", ".join(sorted(consequent)),
                        "Support": support_xy,
                        "Confidence": confidence,
                        "Lift": lift
                    })

    rules.sort(key=lambda rule: rule["Confidence"], reverse=True)
    return rules


def itemsets_dataframe(frequent_itemsets):
    """Return a DataFrame of frequent itemsets with readable formatting."""
    rows = [
        {
            "Itemset": ", ".join(sorted(itemset)),
            "Length": len(itemset),
            "Support": support
        }
        for itemset, support in frequent_itemsets.items()
    ]

    if not rows:
        return pd.DataFrame(columns=["Itemset", "Length", "Support"])

    return pd.DataFrame(rows).sort_values(
        ["Length", "Support"], ascending=[True, False]
    ).reset_index(drop=True)


def parse_args():
    parser = argparse.ArgumentParser(description="Apriori association-rule mining for CICIDS2017-style itemset data.")
    parser.add_argument("--csv", default="preprocessed_cicids2017.csv", help="Path to the CSV dataset.")
    parser.add_argument("--sample-size", type=int, default=None, help="Number of rows to read for testing; default uses full dataset.")
    parser.add_argument("--min-support", type=float, default=0.05, help="Minimum support threshold in the range (0, 1].")
    parser.add_argument("--min-confidence", type=float, default=0.60, help="Minimum confidence threshold in the range (0, 1].")
    parser.add_argument("--min-lift", type=float, default=1.0, help="Minimum lift threshold.")
    parser.add_argument("--include-label", action="store_true", help="Keep the Label column as an item. Usually disabled to avoid label-driven rules.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    transactions = load_transactions(
        args.csv,
        sample_size=args.sample_size,
        include_label=args.include_label
    )

    frequent = apriori(transactions, args.min_support)
    rules = generate_rules(frequent, args.min_confidence, args.min_lift)
    itemsets_df = itemsets_dataframe(frequent)
    rules_df = pd.DataFrame(rules)

    print("\nFrequent itemsets found:", len(frequent))
    print("Association rules found:", len(rules))

    print("\nTop frequent itemsets:")
    if itemsets_df.empty:
        print("No frequent itemsets found for the selected support threshold.")
    else:
        print(itemsets_df.head(20).to_string(index=False))

    print("\nTop association rules:")
    if rules_df.empty:
        print("No rules satisfy the selected thresholds.")
    else:
        print(rules_df.head(20).to_string(index=False))

    itemsets_df.to_csv("frequent_itemsets.csv", index=False)
    rules_df.to_csv("association_rules.csv", index=False)

    print("\nResults saved to CSV files.")
