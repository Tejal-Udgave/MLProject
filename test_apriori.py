
import pandas as pd
import os

# --------------------------------------------------
# 1. File paths
# --------------------------------------------------

CSV_PATH = "preprocessed_cicids2017.csv"
ITEMSETS_PATH = "frequent_itemsets.csv"
RULES_PATH = "association_rules.csv"

# --------------------------------------------------
# 2. Load and inspect the dataset
# --------------------------------------------------

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Dataset not found: {CSV_PATH}")

df = pd.read_csv(CSV_PATH, low_memory=False)

print("=" * 55)
print("DATASET INFORMATION")
print("=" * 55)

print("Dataset shape:", df.shape)
print("Total records:", len(df))
print("Total columns:", len(df.columns))

# --------------------------------------------------
# 3. Check label distribution
# --------------------------------------------------

if "Label" in df.columns:
    print("\n" + "=" * 55)
    print("LABEL DISTRIBUTION (COUNTS)")
    print("=" * 55)

    print(df["Label"].value_counts(dropna=False))

    print("\n" + "=" * 55)
    print("LABEL DISTRIBUTION (PROPORTIONS)")
    print("=" * 55)

    print(
        df["Label"]
        .value_counts(normalize=True, dropna=False)
        .round(4)
    )

else:
    print("\nWARNING: Label column not found.")

# --------------------------------------------------
# 4. Inspect frequent itemsets
# --------------------------------------------------

if os.path.exists(ITEMSETS_PATH):
    itemsets = pd.read_csv(ITEMSETS_PATH)

    print("\n" + "=" * 55)
    print("FREQUENT ITEMSET RESULTS")
    print("=" * 55)

    print("Total frequent itemsets:", len(itemsets))

    if not itemsets.empty:
        print("\nTop 10 frequent itemsets:")
        print(
            itemsets.sort_values(
                "Support", ascending=False
            ).head(10).to_string(index=False)
        )
else:
    print("\nFrequent itemsets file not found.")

# --------------------------------------------------
# 5. Inspect association rules
# --------------------------------------------------

if os.path.exists(RULES_PATH):
    rules = pd.read_csv(RULES_PATH)

    print("\n" + "=" * 55)
    print("ASSOCIATION RULE RESULTS")
    print("=" * 55)

    print("Total association rules:", len(rules))

    if not rules.empty:
        print("\nTop 10 rules by confidence:")
        print(
            rules.sort_values(
                "Confidence", ascending=False
            ).head(10).to_string(index=False)
        )

        print(
            "\nRules with confidence = 1.0:",
            (rules["Confidence"] >= 0.999999).sum()
        )

        print(
            "Rules with lift > 1.2:",
            (rules["Lift"] > 1.2).sum()
        )
else:
    print("\nAssociation rules file not found.")

print("\nInspection complete.")
