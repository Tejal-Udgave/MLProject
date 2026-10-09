
from collections import Counter

# Small dataset with results we can calculate by hand
transactions = [
    {"A", "B"},
    {"A", "B"},
    {"A"},
    {"B"},
]

total = len(transactions)

def support(itemset):
    count = sum(
        1 for transaction in transactions
        if itemset.issubset(transaction)
    )
    return count / total

# Expected supports
support_a = support({"A"})
support_b = support({"B"})
support_ab = support({"A", "B"})

# Confidence and lift for A -> B
confidence_a_to_b = support_ab / support_a
lift_a_to_b = confidence_a_to_b / support_b

# Verify expected values
assert abs(support_a - 0.75) < 1e-9
assert abs(support_b - 0.75) < 1e-9
assert abs(support_ab - 0.50) < 1e-9
assert abs(confidence_a_to_b - (2 / 3)) < 1e-9
assert abs(lift_a_to_b - (8 / 9)) < 1e-9

print("All measure tests passed!")
print(f"Support(A): {support_a:.4f}")
print(f"Support(B): {support_b:.4f}")
print(f"Support(A, B): {support_ab:.4f}")
print(f"Confidence(A -> B): {confidence_a_to_b:.4f}")
print(f"Lift(A -> B): {lift_a_to_b:.4f}")
