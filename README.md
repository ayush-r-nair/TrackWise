## TrackWise – AI Expense Tracker

TrackWise is a small AI-powered tool that helps you **categorize expenses from receipts**, **analyze your spending patterns**, and **generate budgeting advice** using a multi‑agent CrewAI workflow running on a local Ollama model.

The core entrypoint is `run.py`, which reads your expenses data, calls a set of specialized agents defined in `agents.py`, and writes a summary analysis back to disk.

---

## Features

- **Receipt categorization**: Classifies each expense into categories such as Groceries, Food & Drinks, Electronics, Medical & Pharmacy, etc.
- **Spending analysis**: Aggregates spending by category, total spent, and number of receipts.
- **Budget advice**: Generates student‑friendly budgeting tips and a “quick win” recommendation.
- **Incremental runs**: Skips receipts that were already analyzed in a previous run, so you can keep adding new data over time.

---

## Project structure (key files)

- `run.py` – Main script that:
  - Loads expenses from `outputs/expenses.json`
  - Runs the CrewAI agents (categorizer, analyzer, advisor)
  - Writes results to `outputs/crew_analysis.json`
  - Prints a short summary to the console
- `agents.py` – Defines:
  - `ExpenseAgents`: three agents (categorizer, analyzer, advisor) configured to talk to your local LLM
  - `ExpenseTasks`: tasks that describe how each agent should behave and what JSON it must return
- `outputs/expenses.json` – Input data file containing your receipts/expenses.
- `outputs/crew_analysis.json` – Output file with categorization, analysis, and advice.

You may also have `manual/` and `temp/` directories locally; these are intentionally **not** tracked in git.

---

## Tech stack

- **Python**
- **CrewAI** for multi‑agent orchestration
- **LangChain Ollama (`langchain_ollama`)** for talking to a local model
- **Ollama** with the `llama3.1` model (or a compatible chat model)

---

## Prerequisites

- Python 3.10+ (recommended)
- [Ollama](https://ollama.com) installed and running locally
- The model used in code is `ollama/llama3.1`, so make sure to pull it:

```bash
ollama pull llama3.1
```

---

## Installation

From the project root (`TrackWise`):

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install crewai langchain-ollama
```

If you have additional dependencies, install them here as well.

---

## Input data format (`outputs/expenses.json`)

`run.py` expects a JSON file at `outputs/expenses.json` with a list of expense objects. A minimal example:

```json
[
  {
    "image_file": "receipt_001.jpg",
    "merchant": "SuperMart",
    "total": 123.45
  },
  {
    "image_file": "receipt_002.jpg",
    "merchant": "Coffee Shop",
    "total": 45.00
  }
]
```

- `image_file`: A unique identifier for the receipt (often the filename of the scanned image).
- `merchant`: Store or vendor name.
- `total`: Numeric amount spent. If `total` is missing or `null`, the code treats it as 0.

`run.py` can be run multiple times; it remembers previously‑categorized receipts using the `categorization` section of `outputs/crew_analysis.json` and only processes **new** ones.

---

## How it works (high level)

1. **Load existing data**
   - Read `outputs/expenses.json`.
   - If `outputs/crew_analysis.json` exists, load prior categorization so old receipts are not reprocessed.
2. **Categorize receipts**
   - `ExpenseAgents.categorizer_agent()` + `ExpenseTasks.categorize_task(...)`.
   - Runs a Crew with a single agent to assign each `image_file` to one of the predefined categories.
3. **Analyze spending**
   - `ExpenseAgents.analyzer_agent()` + `ExpenseTasks.analyze_task(...)`.
   - Aggregates `total_spent` and `by_category`, and asks the model for high‑level insights and anomalies.
4. **Generate advice**
   - `ExpenseAgents.advisor_agent()` + `ExpenseTasks.advise_task(...)`.
   - Produces budgeting advice in strict JSON (budget status, tips, quick win, encouragement).
5. **Save and print results**
   - Writes a combined object with `categorization`, `analysis`, and `advice` into `outputs/crew_analysis.json`.
   - Prints a short summary (total spent, top categories, top tips) to the console.

---

## Usage

From the project root:

```bash
python run.py
```

You should see logs in the terminal showing:

- Number of new receipts to analyze
- Steps (categorization, analysis, advice)
- Final summary and a message pointing to `outputs/crew_analysis.json`

---

