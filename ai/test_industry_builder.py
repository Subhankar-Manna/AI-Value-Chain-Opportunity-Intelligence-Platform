from ai.industry_builder import build_industry


result = build_industry("Automotive")


print("\nIndustry:")
print(result["industry"])

print("\nValue Chain:\n")

for stage in result["stages"]:

    print(f"Stage: {stage['stage_name']}")
    print(f"Description: {stage['stage_description']}")

    for process in stage["processes"]:
        print(
            f"  - {process['process_name']}: "
            f"{process['process_description']}"
        )

    print()