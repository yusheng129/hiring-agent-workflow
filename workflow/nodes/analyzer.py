"""Analysis and scoring node.

Input:  extracted_data (structured dict from extractor)
Output: analysis_result (tags, match_score, risk_points)
"""

import json
import re
from workflow.state import AgentState


def analyzer_node(state: AgentState) -> AgentState:
    """Analyze extracted data and generate tags, match score, and risk points."""
    import anthropic
    import os

    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY") or os.getenv("MINIMAX_API_KEY") or "dummy",
        base_url="https://api.minimaxi.com/anthropic"
    )

    extracted = state.extracted_data
    if not extracted or "error" in extracted:
        state.analysis_result = {"error": "No valid extracted data"}
        return state

    # Build analysis prompt based on input type
    if state.input_type == "candidate":
        prompt = f"""你是一个专业的面试官，请根据以下候选人信息进行评估：

候选人信息：
{json.dumps(extracted, ensure_ascii=False, indent=2)}

jd_text (参考):
{state.jd_text or "未提供"}

请以 JSON 格式输出评估结果，只输出纯 JSON，不要任何 markdown 标记：
{{
  "tags": ["标签1", "标签2"],
  "match_score": 85,
  "score_reason": "评分理由说明",
  "risk_points": [
    {{"point": "风险点描述", "severity": "high"}}
  ]
}}"""
    else:
        prompt = f"""你是一个资深项目经理，请根据以下项目信息进行评估：

项目信息：
{json.dumps(extracted, ensure_ascii=False, indent=2)}

请以 JSON 格式输出评估结果，只输出纯 JSON，不要任何 markdown 标记：
{{
  "tags": ["标签1", "标签2"],
  "match_score": 85,
  "score_reason": "评分理由说明",
  "risk_points": [
    {{"point": "风险点描述", "severity": "high"}}
  ]
}}"""

    try:
        response = client.messages.create(
            model="MiniMax-M2.7",
            max_tokens=2000,
            system="你是一个专业的评估助手，请只输出纯 JSON，不要 markdown 标记。",
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

        # Clean JSON: remove markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        # Remove any non-JSON characters (like Chinese quotes, extra whitespace)
        content = content.strip()

        # Try to parse JSON, with fallback for common issues
        try:
            analysis = json.loads(content)
        except json.JSONDecodeError as e:
            # Try to fix common JSON issues
            # Replace Chinese quotes with standard quotes
            content = content.replace(""", '"').replace(""", '"').replace("`", "")
            # Remove any trailing commas
            content = re.sub(r',\s*}', '}', content)
            content = re.sub(r',\s*]', ']', content)
            try:
                analysis = json.loads(content)
            except:
                # Last resort: extract JSON object using regex
                match = re.search(r'\{[\s\S]*\}', content)
                if match:
                    analysis = json.loads(match.group())
                else:
                    raise e

        analysis["input_type"] = state.input_type

        state.analysis_result = analysis
        state.add_log(f"Analyzed: match_score={analysis.get('match_score', 'N/A')}, tags={len(analysis.get('tags', []))}")

    except Exception as e:
        state.analysis_result = {"error": str(e), "input_type": state.input_type}
        state.add_log(f"Analysis failed: {str(e)}")

    return state
