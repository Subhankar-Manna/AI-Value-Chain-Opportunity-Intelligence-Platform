from .priority import calculate_priority


result = calculate_priority(
    value_score=9,
    feasibility_score=8,
    risk_score=3,
    confidence_score=8
)

print("\nPRIORITY ANALYSIS\n")
print(result)