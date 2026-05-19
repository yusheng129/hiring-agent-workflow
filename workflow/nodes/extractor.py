"""Information extraction node.

Input:  raw text (resume or project document)
Output: extracted_data (structured dict)
"""

import json
from workflow.state import AgentState
from schema.models import SkillTag


def build_extraction_prompt(text: str, input_type: str) -> str:
    """Build prompt for LLM extraction based on input type."""
    if input_type == "candidate":
        return f"""你是一个专业 HR，请从以下简历文本中抽取关键信息，以 JSON 格式输出：

输入文本：
{text}

输出格式（只输出 JSON，不要其他内容）：
{{
  "name": "姓名（未找到填 null）",
  "age": 年龄数字（未找到填 null）,
  "education": "学历（未找到填 null）",
  "work_years": 工作年限数字（未找到填 null）",
  "current_company": "当前公司（未找到填 null）",
  "current_title": "当前职位（未找到填 null）",
  "skills": ["技能1", "技能2", ...],
  "project_experience": ["项目1描述", "项目2描述", ...],
  "expected_salary": "薪资预期（未找到填 null）"
}}"""
    else:
        return f"""你是一个项目经理，请从以下项目文档中抽取关键信息，以 JSON 格式输出：

输入文本：
{text}

输出格式（只输出 JSON，不要其他内容）：
{{
  "project_name": "项目名称",
  "industry": "行业领域（未找到填 null）",
  "tech_stack": ["技术1", "技术2", ...],
  "core_metrics": ["核心指标1", "核心指标2", ...],
  "risk_points": ["风险点1", "风险点2", ...],
  "delivery_time": "交付时间（未找到填 null）",
  "team_size": 团队人数（未找到填 null）
}}"""


def extractor_node(state: AgentState) -> AgentState:
    """Extract structured data from raw text using LLM."""
    import anthropic
    import os

    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY") or os.getenv("MINIMAX_API_KEY") or "dummy",
        base_url="https://api.minimaxi.com/anthropic"
    )

    prompt = build_extraction_prompt(state.input_text, state.input_type)

    try:
        response = client.messages.create(
            model="MiniMax-M2.7",
            max_tokens=2000,
            system="你是一个专业的 HR 助手，请严格按 JSON 格式输出。",
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

        # Try to extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        elif content.startswith("{"):
            content = content

        extracted = json.loads(content)

        # Normalize skills format
        if state.input_type == "candidate" and "skills" in extracted:
            skills = extracted["skills"]
            if isinstance(skills, list):
                extracted["skills"] = [{"name": s, "confidence": 0.8} if isinstance(s, str) else s for s in skills]

        state.extracted_data = extracted
        state.add_log(f"Extracted {len(extracted)} fields from {state.input_type} input")

    except Exception as e:
        state.extracted_data = {"error": str(e), "raw_text": state.input_text[:500]}
        state.add_log(f"Extraction failed: {str(e)}")

    return state
