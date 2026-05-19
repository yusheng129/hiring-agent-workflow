"""Action recommendation node.

Input:  analysis_result (from analyzer)
Output: recommendation (next_action, follow_up_questions)
"""

import json
from workflow.state import AgentState


def advisor_node(state: AgentState) -> AgentState:
    """Generate next action and follow-up questions based on analysis."""
    import anthropic
    import os

    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY") or os.getenv("MINIMAX_API_KEY") or "dummy",
        base_url="https://api.minimaxi.com/anthropic"
    )

    analysis = state.analysis_result
    if not analysis or "error" in analysis:
        state.final_output = {"error": "No valid analysis result"}
        return state

    # Build recommendation prompt
    if state.input_type == "candidate":
        prompt = f"""你是一个专业 HR，请根据以下评估结果给出行动建议：

评估结果：
{json.dumps(analysis, ensure_ascii=False, indent=2)}

候选人原始信息摘要：
{json.dumps(state.extracted_data, ensure_ascii=False, indent=2)[:500]}...

请以 JSON 格式输出行动建议：
{{
  "next_action": "下一步动作（如：安排技术面、进入人才池、推荐其他岗位等）",
  "next_action_reason": "给出这个建议的理由",
  "follow_up_questions": [
    "问题1：针对风险点或模糊处的追问",
    "问题2",
    "问题3"
  ],
  "suggested_tags": ["建议添加的标签1", ...]
}}

要求：
- 追问必须针对风险点或信息不明确处
- 下一个动作要具体可执行
- 问题数量 3-5 个"""
    else:
        prompt = f"""你是一个资深项目经理，请根据以下项目评估给出行动建议：

评估结果：
{json.dumps(analysis, ensure_ascii=False, indent=2)}

项目原始信息摘要：
{json.dumps(state.extracted_data, ensure_ascii=False, indent=2)[:500]}...

请以 JSON 格式输出行动建议：
{{
  "next_action": "下一步动作（如：安排项目演示、技术评审、进入迭代等）",
  "next_action_reason": "给出这个建议的理由",
  "follow_up_questions": [
    "问题1：针对风险点或模糊处的追问",
    "问题2",
    "问题3"
  ],
  "suggested_tags": ["建议添加的标签1", ...]
}}

要求：
- 追问必须针对风险点
- 下一个动作要具体可执行
- 问题数量 3-5 个"""

    try:
        response = client.messages.create(
            model="MiniMax-M2.7",
            max_tokens=2000,
            system="你是一个专业的 HR/项目经理助手，请严格按 JSON 格式输出。",
            messages=[
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ]
        )

        # Extract text from response content
        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        content = content.strip()

        # Extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        recommendation = json.loads(content)

        # Build final output
        state.final_output = {
            "input_type": state.input_type,
            "extracted_data": state.extracted_data,
            "analysis": analysis,
            "recommendation": recommendation,
            "step_logs": state.step_logs
        }

        state.add_log(f"Generated recommendation: {recommendation.get('next_action', 'N/A')}")

    except Exception as e:
        state.final_output = {"error": str(e), "step_logs": state.step_logs}
        state.add_log(f"Recommendation failed: {str(e)}")

    return state
