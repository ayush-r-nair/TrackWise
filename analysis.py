import json

CREW_OUTPUT = "outputs/crew_analysis.json"

with open(CREW_OUTPUT, "r") as f:
    data = json.load(f)

categorization = data["categorization"]
analysis = data["analysis"]
advice = data["advice"]

print("\n" + "="*70)
print("EXPENSE REPORT WITH AI INSIGHTS")
print("="*70)

print(f"\n💰 TOTAL SPENT: ₹{analysis.get('total_spent', 0):.2f}")

print("\n📊 BY CATEGORY:")
for cat, amt in sorted(analysis.get('by_category', {}).items(), key=lambda x: x[1], reverse=True):
    pct = (amt / analysis['total_spent'] * 100) if analysis['total_spent'] else 0
    print(f"  {cat:25s}  ₹{amt:8.2f}  ({pct:5.1f}%)")

print("\n🔍 INSIGHTS:")
for insight in analysis.get('insights', []):
    print(f"  • {insight}")

print("\n💡 BUDGET ADVICE:")
print(f"Status: {advice.get('budget_status', 'N/A')}")
print("\nTips:")
for tip in advice.get('tips', []):
    print(f"  • {tip}")

print(f"\n⚡ Quick Win: {advice.get('quick_win', 'N/A')}")
print(f"\n✅ {advice.get('positive', 'Keep tracking your expenses!')}")
