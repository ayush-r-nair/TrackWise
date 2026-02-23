import json
import re
import os
from agents import ExpenseAgents, ExpenseTasks
from crewai import Crew, Process

EXPENSES_FILE = "outputs/expenses.json"
OUTPUT_FILE = "outputs/crew_analysis.json"

def clean_json_response(text):
    text = str(text)
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    start = text.find('{')
    end = text.rfind('}') + 1
    if start != -1 and end > start:
        json_str = text[start:end]
        try:
            return json.loads(json_str)
        except:
            return None
    return None


def run_expense_crew():
    with open(EXPENSES_FILE, "r") as f:
        expenses = json.load(f)

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            old_data = json.load(f)
            old_categorization = old_data.get("categorization", {})
    else:
        old_categorization = {}

    new_expenses = [e for e in expenses if e['image_file'] not in old_categorization]

    if not new_expenses:
        print("No new receipts to analyze. Skipping.")
        return old_data

    print(f"Found {len(new_expenses)} new receipts to analyze.\n")
    print("="*70)
    print("STARTING CREWAI MULTI-AGENT ANALYSIS")
    print("="*70 + "\n")

    agents = ExpenseAgents()
    tasks_obj = ExpenseTasks()

    categorizer = agents.categorizer_agent()
    analyzer = agents.analyzer_agent()
    advisor = agents.advisor_agent()

    print("Step 1: Categorizing NEW expenses...")

    categorize_task = tasks_obj.categorize_task(categorizer, new_expenses)

    crew1 = Crew(
        agents=[categorizer],
        tasks=[categorize_task],
        process=Process.sequential,
        verbose=False
    )

    cat_result = crew1.kickoff()

    categorization_new = clean_json_response(cat_result)
    categorization = {**old_categorization, **categorization_new}

    print(f"Categorized {len(categorization_new)} new receipts\n")

    print("Step 2: Analyzing spending patterns...")
    analyze_task = tasks_obj.analyze_task(analyzer, expenses, categorization)

    crew2 = Crew(
        agents=[analyzer],
        tasks=[analyze_task],
        process=Process.sequential,
        verbose=False
    )

    analysis_result = crew2.kickoff()
    analysis = clean_json_response(analysis_result)

    if not analysis:
        total = sum((e.get('total') or 0) for e in expenses)
        analysis = {"total_spent": total, "insights": [], "anomalies": []}

    print(f"Found {len(analysis.get('insights', []))} insights\n")

    print("Step 3: Generating budget advice...")
    advise_task = tasks_obj.advise_task(advisor, analysis)

    crew3 = Crew(
        agents=[advisor],
        tasks=[advise_task],
        process=Process.sequential,
        verbose=False
    )

    advice_result = crew3.kickoff()
    advice = clean_json_response(advice_result)

    if not advice:
        advice = {"tips": [], "quick_win": "Track your spending daily"}

    final_output = {
        "categorization": categorization,
        "analysis": analysis,
        "advice": advice
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_output, f, indent=2)

    print("="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nResults saved to: {OUTPUT_FILE}")

    print("\n--- SUMMARY ---")
    print(f"Total Spent: ₹{analysis.get('total_spent', 0)}")
    print(f"\nTop Categories:")
    for cat, amt in list(analysis.get('by_category', {}).items())[:3]:
        print(f"  {cat}: ₹{amt}")

    print(f"\nTop Tips:")
    for tip in advice.get('tips', [])[:3]:
        print(f"  - {tip}")

    return final_output


if __name__ == "__main__":
    run_expense_crew()
