import asyncio
import json
import sqlite3
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# --- Core Logic: Hierarchical Reconciliation ---

class ReconciliationEngine:
    """
    Implements a Bottom-Up reconciliation strategy for hierarchical time series.
    """
    @staticmethod
    def reconcile(bottom_level_forecasts: Dict[str, float], hierarchy_map: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Aggregates bottom-level forecasts to parent nodes.
        hierarchy_map: {parent: [child1, child2, ...]}
        """
        results = bottom_level_forecasts.copy()
        for parent, children in hierarchy_map.items():
            results[parent] = sum(results.get(child, 0.0) for child in children)
        return results

# --- Database Layer ---

class Database:
    def __init__(self, db_path: str = "reconciler.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS forecasts (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    data TEXT
                )
            """)

    def save_forecast(self, data: Dict[str, float]):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO forecasts VALUES (?, ?, ?)",
                (str(uuid.uuid4()), datetime.utcnow().isoformat(), json.dumps(data))
            )

# --- Web Application ---

app = FastAPI(title="Hierarchical Reconciler")
db = Database()
engine = ReconciliationEngine()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #09090B; color: #FAFAFA; font-family: 'Inter', sans-serif; }
        .card { background-color: #121214; border: 1px solid #27272A; }
        .mono { font-family: 'ui-monospace', monospace; }
    </style>
</head>
<body class="p-8">
    <div class="max-w-4xl mx-auto">
        <header class="mb-8">
            <h1 class="text-2xl font-bold tracking-tight">Hierarchical Reconciler</h1>
            <p class="text-zinc-500 text-sm">Bottom-up aggregation engine</p>
        </header>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="card p-6 rounded-xl">
                <form action="/reconcile" method="post" class="space-y-4">
                    <div>
                        <label class="block text-xs uppercase tracking-widest text-zinc-500 mb-2">Bottom Forecasts (JSON)</label>
                        <textarea name="forecasts" class="w-full bg-black border border-zinc-800 rounded p-3 mono text-sm h-32" placeholder='{"A": 10, "B": 20}'></textarea>
                    </div>
                    <div>
                        <label class="block text-xs uppercase tracking-widest text-zinc-500 mb-2">Hierarchy (JSON)</label>
                        <textarea name="hierarchy" class="w-full bg-black border border-zinc-800 rounded p-3 mono text-sm h-32" placeholder='{"Total": ["A", "B"]}'></textarea>
                    </div>
                    <button type="submit" class="w-full bg-white text-black font-medium py-2 rounded hover:bg-zinc-200 transition">Reconcile</button>
                </form>
            </div>
            
            <div class="card p-6 rounded-xl">
                <h2 class="text-xs uppercase tracking-widest text-zinc-500 mb-4">Output</h2>
                <pre class="text-emerald-400 mono text-sm overflow-auto">{{ result }}</pre>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_TEMPLATE.replace("{{ result }}", "Waiting for input...")

@app.post("/reconcile", response_class=HTMLResponse)
async def reconcile_post(forecasts: str = Form(...), hierarchy: str = Form(...)):
    try:
        f_data = json.loads(forecasts)
        h_data = json.loads(hierarchy)
        
        result = engine.reconcile(f_data, h_data)
        db.save_forecast(result)
        
        return HTML_TEMPLATE.replace("{{ result }}", json.dumps(result, indent=4))
    except Exception as e:
        return HTML_TEMPLATE.replace("{{ result }}", f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)