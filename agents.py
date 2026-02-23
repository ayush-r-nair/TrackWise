from crewai import Agent, Task,LLM, Crew, Process
from langchain_ollama import ChatOllama
import json

llm = LLM(
    model="ollama/llama3.1", 
    base_url="http://localhost:11434"
)

CATEGORIES = [
    "Groceries",
    "Food & Drinks", 
    "Snacks",
    "Household Supplies",
    "Toiletries & Personal Care",
    "Electronics",
    "Medical & Pharmacy",
    "Clothing & Apparel",
    "Other"
]


class ExpenseAgents:
    def __init__(self):
        self.llm = llm
    
    def categorizer_agent(self):
        return Agent(
            role="Expense Categorization Expert",
            goal="Accurately categorize receipts into appropriate spending categories",
            backstory="""You are an expert at analyzing receipts and categorizing expenses.
            You understand context and always return valid JSON.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def analyzer_agent(self):
        return Agent(
            role="Spending Pattern Analyst",
            goal="Identify spending trends and patterns",
            backstory="""You are a financial analyst who finds patterns in spending data.
            You always return structured JSON with insights.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def advisor_agent(self):
        return Agent(
            role="Personal Finance Advisor",
            goal="Provide actionable budgeting advice for students",
            backstory="""You are a financial advisor for students. 
            You provide practical tips in JSON format.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )


class ExpenseTasks:
    def categorize_task(self, agent, expenses):
        expenses_text = "\n".join([
            f"- {e['image_file']}: {e['merchant']}, ₹{e['total']}"
            for e in expenses
        ])
        
        return Task(
            description=f"""Categorize these receipts:
            
            {expenses_text}
            
            For each receipt, choose ONE category from: {', '.join(CATEGORIES)}
            
            Return ONLY valid JSON (no markdown, no explanation):
            {{
              "receipt1.jpg": {{
                "category": "Groceries",
                "confidence": 95,
                "reasoning": "brief reason"
              }}
            }}
            """,
            agent=agent,
            expected_output="Valid JSON object with categorization"
        )
    
    def analyze_task(self, agent, expenses, categorization):
        by_category = {}
        total_spent = 0
        
        for e in expenses:
            img = e['image_file']
            cat = categorization.get(img, {}).get('category', 'Other')
            
            # Safely handle None values
            expense_total = e.get('total')
            if expense_total is None:
                expense_total = 0
            
            by_category[cat] = by_category.get(cat, 0) + expense_total
            total_spent += expense_total
        
        analysis_data = f"""
        Total spent: ₹{total_spent:.2f}
        By category: {json.dumps(by_category, indent=2)}
        Number of receipts: {len(expenses)}
        """
        
        return Task(
            description=f"""Analyze this spending data:
            
            {analysis_data}
            
            Provide insights about spending patterns.
            
            Return ONLY valid JSON (no markdown):
            {{
            "total_spent": {total_spent},
            "by_category": {json.dumps(by_category)},
            "insights": ["insight1", "insight2", "insight3"],
            "anomalies": ["any unusual spending"]
            }}
            """,
            agent=agent,
            expected_output="Valid JSON with analysis"
        )
    
    def advise_task(self, agent, analysis):
        return Task(
            description=f"""Based on this analysis:
            
            {json.dumps(analysis, indent=2)}
            
            Provide budget advice for a student.
            
            Return ONLY valid JSON (no markdown):
            {{
              "budget_status": "on track/over budget/under budget",
              "tips": ["tip1", "tip2", "tip3"],
              "quick_win": "one actionable step",
              "positive": "encouragement"
            }}
            """,
            agent=agent,
            expected_output="Valid JSON with advice"
        )