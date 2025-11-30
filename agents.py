# agents.py
from typing import Dict, Any
from memory import InMemorySessionService, VectorStore
from tools import identify_food, lookup_nutrition, generate_meal_plan, run_judge
from observability import log, metric, get_logs, get_metrics
from mcp import start_lro, resume_lro, list_pending
import json, time

session_service = InMemorySessionService()
memory_store = VectorStore()
nutrition_df = None  # will be injected by orchestrator or higher-level code

def orchestrator_start(image_bytes: bytes, profile: Dict[str, Any], user_id: str = 'demo_user', nutrition_dataframe=None) -> Dict[str, Any]:
    global nutrition_df
    if nutrition_dataframe is not None:
        nutrition_df = nutrition_dataframe
    session = session_service.create(user_id, profile)
    sid = session['session_id']
    trace_id = f'trace_{sid}_{int(time.time())}'
    log('orchestrator', 'start', {'session_id': sid})

    # Vision
    vision = identify_food(image_bytes)
    log('vision_agent', 'identify_food', vision)
    food = vision['items'][0]

    # Nutrition
    nutrition = lookup_nutrition(food['food_id'], memory_store, nutrition_df)
    log('nutrition_agent', 'lookup_nutrition', nutrition)

    # Planner
    plan = generate_meal_plan(profile, food)
    log('planner_agent', 'generate_meal_plan', {'plan_id': plan.get('plan_id')})

    # Judge
    judge = run_judge(plan, profile)
    log('judge_agent', 'run_judge', judge)

    if judge.get('overall', 100) < 60:
        op_id = start_lro(sid, {'plan': plan, 'judge': judge}, reason='low_score')
        session_service.sessions[sid].setdefault('paused_ops', []).append(op_id)
        log('orchestrator', 'paused_for_approval', {'op_id': op_id})
        return {'status': 'paused', 'op_id': op_id, 'plan': plan, 'judge': judge, 'trace_id': trace_id}

    # Save plan
    memory_store.add(json.dumps(plan), metadata={'user_id': user_id, 'plan_id': plan.get('plan_id')})
    log('orchestrator', 'finalize_plan', {'plan_id': plan.get('plan_id')})
    return {'status': 'done', 'plan': plan, 'judge': judge, 'trace_id': trace_id}

def resume_approval(op_id: str) -> Dict[str, Any]:
    res = resume_lro(op_id, {'approved': True})
    log('orchestrator', 'resumed_op', {'op_id': op_id})
    return res

def get_pending_ops():
    return list_pending()

def get_observability():
    return {'logs': get_logs(), 'metrics': get_metrics()}
