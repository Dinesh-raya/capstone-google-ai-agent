# tools.py
from typing import Dict, Any, List
from observability import log, metric
from memory import VectorStore
import json

# Note: tools are stubbed for offline demo. Replace with real model/tool calls for production.

def identify_food(image_bytes: bytes) -> Dict[str, Any]:
    metric('vision')
    log('vision_agent', 'identify_food', {'note': 'stub'})
    return {
        'items': [{'food_id': 'chicken_salad', 'label': 'Chicken Salad', 'confidence': 0.93}],
        'total_calories': 420
    }

def lookup_nutrition(food_id: str, memory_store: VectorStore, nutrition_df=None) -> Dict[str, Any]:
    metric('rag')
    log('nutrition_agent', 'lookup_nutrition', {'food_id': food_id})
    # Try vector RAG
    results = memory_store.query('chicken salad', top_k=1)
    if results:
        return results[0]['metadata']
    # Fallback: use provided dataframe if available (passed by orchestrator)
    if nutrition_df is not None:
        r = nutrition_df[nutrition_df['food_id'] == food_id]
        if not r.empty:
            return r.iloc[0].to_dict()
    return {'food_id': food_id, 'calories': None}

def generate_meal_plan(profile: Dict[str, Any], seed_item: Dict[str, Any]) -> Dict[str, Any]:
    metric('plan')
    target = profile.get('target_calories', 2000)
    log('planner_agent', 'generate_plan', {'target': target})
    days = []
    for d in range(3):
        days.append({'day': d+1, 'meals': [
            {'meal': 'breakfast', 'menu': 'Oatmeal + fruit', 'calories': int(target*0.25)},
            {'meal': 'lunch', 'menu': seed_item.get('label', 'Chicken Salad'), 'calories': int(target*0.35)},
            {'meal': 'dinner', 'menu': 'Grilled Fish', 'calories': int(target*0.40)}
        ]})
    return {'plan_id': 'plan_stub_001', 'daily_calories': target, 'days': days, 'rationale': 'Balanced simple plan (stub).'}

def run_judge(plan: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    metric('judge')
    # naive scoring: within 20% of target => good
    target = profile.get('target_calories', 2000)
    daily = plan.get('daily_calories', target)
    diff_pct = abs(daily - target) / target
    overall = 90 if diff_pct < 0.2 else 50
    log('judge_agent', 'run_judge', {'overall': overall})
    return {'overall': overall, 'notes': 'Stubbed judge result.'}
