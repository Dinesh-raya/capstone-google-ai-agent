# app_gradio.py
import gradio as gr
import json, io
from agents import orchestrator_start, resume_approval, get_pending_ops, get_observability, memory_store
import pandas as pd
from PIL import Image

# Provide a small nutrition dataframe for the demo
nutrition_df = pd.DataFrame([
    {'food_id': 'chicken_salad', 'name': 'Chicken Salad', 'calories': 420, 'protein': 30, 'fat': 15, 'carbs': 20},
    {'food_id': 'grilled_fish', 'name': 'Grilled Fish', 'calories': 350, 'protein': 40, 'fat': 8, 'carbs': 5},
    {'food_id': 'oatmeal', 'name': 'Oatmeal', 'calories': 300, 'protein': 10, 'fat': 6, 'carbs': 52},
    {'food_id': 'veggie_salad', 'name': 'Veggie Salad', 'calories': 180, 'protein': 5, 'fat': 7, 'carbs': 20}
])

# Preload nutrition facts into memory_store for RAG
for _, row in nutrition_df.iterrows():
    txt = f"{row['name']} {row['calories']} calories protein {row['protein']} fat {row['fat']} carbs {row['carbs']}"
    memory_store.add(txt, metadata=row.to_dict())

def format_result(res):
    """Convert JSON result to user-friendly Markdown"""
    if 'error' in res:
        return f"## ❌ Error\n\n{res['error']}"
    
    status = res.get('status', 'unknown')
    plan = res.get('plan', {})
    judge = res.get('judge', {})
    
    # Build the markdown output
    md = "# 📊 Your Meal Analysis\n\n"
    
    # Status indicator
    if status == 'done':
        md += "## ✅ Status: Complete\n\n"
    elif status == 'paused':
        md += "## ⚠️ Status: Awaiting Approval\n\n"
        md += f"**Operation ID:** `{res.get('op_id', 'N/A')}`\n\n"
    
    # Meal Plan
    if plan:
        md += "## 🍽️ Meal Plan Details\n\n"
        md += f"**Plan ID:** {plan.get('plan_id', 'N/A')}\n\n"
        
        if 'meals' in plan:
            md += "### Daily Meals\n\n"
            for meal in plan['meals']:
                md += f"- **{meal.get('name', 'Meal')}**: {meal.get('calories', 0)} cal\n"
        
        if 'total_calories' in plan:
            md += f"\n**Total Daily Calories:** {plan['total_calories']} kcal\n\n"
    
    # Judge Score
    if judge:
        overall_score = judge.get('overall', 0)
        md += "## 🎯 Quality Score\n\n"
        
        # Visual score indicator
        if overall_score >= 80:
            md += f"### 🌟 Excellent: {overall_score}/100\n\n"
        elif overall_score >= 60:
            md += f"### 👍 Good: {overall_score}/100\n\n"
        else:
            md += f"### ⚠️ Needs Improvement: {overall_score}/100\n\n"
        
        if 'feedback' in judge:
            md += f"**Feedback:** {judge['feedback']}\n\n"
    
    # Trace ID for debugging
    if 'trace_id' in res:
        md += f"\n---\n\n*Trace ID: {res['trace_id']}*"
    
    return md

def process(image, target_cal, protein_goal, carb_limit, fat_limit):
    """Process meal image with user profile"""
    if image is None:
        return "## ❌ Error\n\nPlease upload a meal image."
    
    # Build profile from form inputs
    profile = {
        'target_calories': target_cal,
        'protein_goal': protein_goal,
        'carb_limit': carb_limit,
        'fat_limit': fat_limit
    }
    
    try:
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        res = orchestrator_start(buf.getvalue(), profile, nutrition_dataframe=nutrition_df)
        return format_result(res)
    except Exception as e:
        return f"## ❌ Error\n\n{str(e)}"

def format_pending(ops):
    """Format pending operations as Markdown table"""
    if not ops or len(ops) == 0:
        return "No pending operations."
    
    md = "## Pending Operations\n\n"
    md += "| Operation ID | Reason | Status |\n"
    md += "|--------------|--------|--------|\n"
    
    for op in ops:
        op_id = op.get('op_id', 'N/A')
        reason = op.get('reason', 'N/A')
        status = op.get('status', 'pending')
        md += f"| `{op_id}` | {reason} | {status} |\n"
    
    return md

def approve(op_id):
    """Approve a pending operation"""
    if not op_id:
        return "## ❌ Error\n\nPlease enter an Operation ID."
    
    try:
        res = resume_approval(op_id)
        return f"## ✅ Approved\n\nOperation `{op_id}` has been approved.\n\n{format_result(res)}"
    except Exception as e:
        return f"## ❌ Error\n\n{str(e)}"

def pending():
    """Get pending operations"""
    try:
        ops = get_pending_ops()
        return format_pending(ops)
    except Exception as e:
        return f"## ❌ Error\n\n{str(e)}"

# Custom CSS for better styling
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.primary-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
    font-weight: bold;
}
"""

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🍎 Smart Fitness & Diet Recommender
        ### AI-Powered Meal Analysis & Personalized Nutrition Planning
        
        Upload a meal image and set your nutrition goals to get personalized recommendations!
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("## 📸 Upload Your Meal")
            img = gr.Image(type='pil', label='Meal Image')
            
            gr.Markdown("## 🎯 Your Nutrition Goals")
            with gr.Row():
                target_cal = gr.Number(label='Target Calories', value=2000, minimum=1000, maximum=5000)
                protein_goal = gr.Number(label='Protein Goal (g)', value=150, minimum=0, maximum=500)
            with gr.Row():
                carb_limit = gr.Number(label='Carb Limit (g)', value=200, minimum=0, maximum=500)
                fat_limit = gr.Number(label='Fat Limit (g)', value=70, minimum=0, maximum=200)
            
            run_btn = gr.Button('🚀 Generate Plan', elem_classes='primary-btn', size='lg')
            
            gr.Markdown("## 📋 Results")
            output = gr.Markdown()
            
            run_btn.click(
                process, 
                inputs=[img, target_cal, protein_goal, carb_limit, fat_limit], 
                outputs=output
            )
        
        with gr.Column(scale=1):
            gr.Markdown("## ⏳ Pending Approvals")
            refresh = gr.Button('🔄 Refresh')
            pending_out = gr.Markdown()
            refresh.click(pending, outputs=pending_out)
            
            gr.Markdown("### Approve Operation")
            op_id = gr.Textbox(label='Operation ID', placeholder='Enter operation ID...')
            approve_btn = gr.Button('✅ Approve')
            approve_out = gr.Markdown()
            approve_btn.click(approve, inputs=op_id, outputs=approve_out)

if __name__ == '__main__':
    demo.launch()
