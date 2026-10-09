import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from apriori import apriori, generate_rules

transactions = [
    frozenset(["A", "B"]),
    frozenset(["A", "B"]),
    frozenset(["A"]),
    frozenset(["B"]),
]

# At 50% support, A, B and {A, B} should be frequent
frequent = apriori(transactions, min_support=0.5)

assert abs(frequent[frozenset(["A"])] - 0.75) < 1e-9
assert abs(frequent[frozenset(["B"])] - 0.75) < 1e-9
assert abs(frequent[frozenset(["A", "B"])] - 0.50) < 1e-9

# Confidence(A -> B) = 2/3 and lift = 8/9.
# With minimum lift 0.8, both directional rules should qualify.
rules = generate_rules(
    frequent,
    min_confidence=0.60,
    min_lift=0.80
)

rule_map = {
    (rule["Antecedent"], rule["Consequent"]): rule
    for rule in rules
}

ab = rule_map[("A", "B")]
ba = rule_map[("B", "A")]

assert abs(ab["Confidence"] - (2 / 3)) < 1e-9
assert abs(ab["Lift"] - (8 / 9)) < 1e-9
assert abs(ba["Confidence"] - (2 / 3)) < 1e-9
assert abs(ba["Lift"] - (8 / 9)) < 1e-9

print("All Apriori correctness tests passed!")
print("Frequent itemsets:", len(frequent))
print("Association rules:", len(rules))
print("Confidence:", round(ab["Confidence"], 4))
print("Lift:", round(ab["Lift"], 4))
