# Hiring Agent Workflow

> 招聘/项目运营 AI Agent 工作流 MVP

## 核心功能

输入候选人简历或项目文档，输出：
- **标签**：技能/领域标签
- **匹配度**：0-100 分（含评分理由）
- **风险点**：识别关键风险
- **下一步动作**：可执行的行动建议
- **拟追问问题**：3-5 个针对性问题

---

## 目录结构

```
hiring-agent-workflow/
├── README.md
├── main.py                 # CLI 入口
├── api.py                  # FastAPI（可选）
├── requirements.txt
├── workflow/
│   ├── __init__.py
│   ├── graph.py           # LangGraph 定义
│   ├── state.py           # Pydantic 状态模型
│   └── nodes/
│       ├── extractor.py   # 1. 信息抽取
│       ├── analyzer.py    # 2. 分析与评分
│       └── advisor.py      # 3. 行动建议
├── examples/              # 3 条样例
│   ├── candidate_yyf.md
│   ├── candidate_frontend.md
│   └── project_vtdemo.md
├── schema/
│   └── models.py          # Pydantic 模型
└── tests/
    └── test_e2e.py
```

---

## 工作流设计

### 3 步设计

```
原始文本 → [抽取] → 结构化数据 → [分析] → 评分/标签/风险 → [建议] → 下一步/追问 → 最终输出
```

| 步骤 | 节点名称 | 输入 | 输出 | 为什么单独拆成一步 | 可验证性 |
|------|---------|------|------|------------------|---------|
| 1 | extractor | 原始文本（简历/项目文档） | ExtractedData Pydantic 模型 | 与分析解耦，后续可单独测试抽取质量，替换不同抽取策略 | 人工检查召回率 |
| 2 | analyzer | ExtractedData + 可选 JD | AnalysisResult（标签/匹配度/风险点） | 评分规则可配置，输出可解释，可单独验证评分逻辑 | 对比人工打分 |
| 3 | advisor | AnalysisResult | Recommendation（下一步/追问问题） | 建议逻辑独立，可替换不同面试官风格（激进/保守） | 检查追问是否针对风险点 |

### LangGraph State 契约

```python
class AgentState(TypedDict):
    # 输入
    input_text: str
    input_type: Literal["candidate", "project"]
    jd_text: Optional[str]  # 可选，用于候选人匹配度计算

    # 中间状态
    extracted_data: Optional[dict]
    analysis_result: Optional[dict]

    # 输出
    final_output: Optional[dict]
```

---

## 输出质量判断框架

### 分阶段检查清单

| 阶段 | 检查项 | 量化指标 | 验证方法 | 谁来做 |
|------|--------|---------|---------|--------|
| 1. 信息抽取 | 关键信息是否齐全 | 召回率 ≥ 90% | 人工检查 + 单元测试 | 你 |
| 2. 分析与评分 | 标签是否准确、匹配度是否合理 | 标签覆盖度 ≥ 80%，匹配度与人工打分差异 ≤ 15 分 | 人工对照 JD/项目标准 | 你 |
| 3. 行动建议 | 追问问题是否针对风险点 | 风险点与追问一一对应率 ≥ 90% | 人工检查逻辑链 | 你 |
| 整体 | 输出是否无幻觉，是否可操作 | 幻觉率 ≤ 10% | 人工通读检查 | 你 |

### 3 条样例的质量预期（验收标准）

| 样例 | 输入类型 | 预期匹配度 | 核心风险点 | 预期下一步 |
|------|---------|-----------|-----------|-----------|
| 1 | 候选人（喻彦丰简历） | 85-90 分 | 无大公司经验、毕业时间稍晚 | 安排技术面 |
| 2 | 候选人（纯前端） | 30-40 分 | 无大模型经验、与岗位方向不符 | 进入人才池 |
| 3 | 项目（VT-Demo） | 90 分 | 依赖体积过大、未做生产级优化 | 安排项目演示 |

---

## 工程取舍

| 决策项 | 选择 | 为什么选这个 | 舍弃了什么 | 舍弃的代价 |
|--------|------|------------|-----------|-----------|
| 工作流引擎 | LangGraph | 可追踪状态，节点独立可测试，贴合 AI Agent 主题 | 纯函数链 | 多一点模板代码 |
| 入口 | CLI 优先 + FastAPI 可选 | 24 小时能做完，易演示 | Web UI | 演示效果稍差 |
| 存储 | 纯内存 + 可选 JSON 落盘 | 轻量化，调试方便 | 向量存储、数据库队列 | 无法处理批量任务 |
| LLM 策略 | 单 LLM 流水线 | 简单，易调试，每步输出可单独检查 | 多 Agent 辩论/反思 | 输出多样性稍差 |
| 评分策略 | 规则 + LLM 混合 | 可解释，质量可控 | 端到端黑盒评分 | 需要手写一部分规则 |
| 测试策略 | 3 条样例端到端测试 + 人工检查清单 | 可复现，24 小时内能做完 | 完整单元测试覆盖 | 代码可维护性稍差 |

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

```bash
# MiniMax
export OPENAI_API_KEY="your-minimax-api-key"
export OPENAI_BASE_URL="https://api.minimax.chat/v1"

# 或使用 OpenAI compatible
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

### CLI 使用

```bash
# 分析候选人
python main.py analyze --type candidate --file examples/candidate_yyf.md

# 分析项目
python main.py analyze --type project --file examples/project_vtdemo.md

# 输出到文件
python main.py analyze --type candidate --file examples/candidate_frontend.md --output result.json

# 直接输入文本
python main.py analyze --type candidate --text "5年Python开发经验，熟悉FastAPI和LangGraph"
```

### API 使用（可选）

```bash
# 启动 API 服务
uvicorn api:app --reload --port 8000

# 调用示例
curl -X POST "http://localhost:8000/analyze" \
  -F "input_type=candidate" \
  -F "text=3年前端经验，React/Vue"
```

### 运行测试

```bash
python tests/test_e2e.py
```

---

## 核心设计决策

### 为什么用 LangGraph？

1. **状态可追踪**：每步的输入输出都保存在 state 中，方便调试和回溯
2. **节点独立可测试**：extractor/analyzer/advisor 可以单独测试
3. **扩展性好**：后续可以加条件边（如：低分候选人直接进人才池）

### 为什么每个节点都是单次 LLM 调用？

1. **降低复杂度**：不做多轮对话，避免状态管理麻烦
2. **提高可预测性**：输入→输出单一映射，便于调试
3. **节省成本**：3 次调用 vs 多轮对话的 10+ 次调用

### 评分逻辑怎么做的？

- **规则基准分**：根据工作年限、技能匹配度等硬指标给基准分
- **LLM 调优**：LLM 根据上下文在基准分上做调整，并给出理由
- **可解释性**：每个分数都有文字说明，不是黑盒

---

## AI 协作说明

| 角色 | 负责人 |
|------|--------|
| 架构设计 | 喻彦丰 |
| 代码实现 | Claude |
| 测试与调优 | 喻彦丰 + Claude |
| 录屏演示 | 喻彦丰 |
| 排错记录 | 喻彦丰 |

---

## 排错记录

> 开发过程中遇到的问题及解决方案

### 问题 1: LangGraph 版本兼容

**现象**：`StateGraph` 导入报错或状态传递失败

**原因**：LangGraph 0.3.x 版本的状态传递方式与 0.2.x 不同

**解决**：
```python
# 0.2.x 写法
workflow = StateGraph(AgentState)  # AgentState 是 TypedDict

# 0.3.x 写法（需要用 Pydantic State）
from langgraph.state import StateSchema
workflow = StateGraph(StateSchema(AgentState))
```

本项目使用 `0.2.x` 版本以确保兼容性。

### 问题 2: LLM 输出格式不稳定

**现象**：`json.loads` 失败，因为 LLM 返回了 markdown 格式

**解决**：在 `extractor.py`/`analyzer.py`/`advisor.py` 中增加 JSON 提取逻辑：
```python
if "```json" in content:
    content = content.split("```json")[1].split("```")[0]
elif "```" in content:
    content = content.split("```")[1].split("```")[0]
```

### 问题 3: 角色扮演导致输出不稳定

**现象**：`analyzer_node` 中偶尔出现非 JSON 输出

**原因**：系统 prompt 中要求 JSON，但用户 prompt 中有角色扮演内容干扰

**解决**：分离系统 prompt（纯格式要求）和用户 prompt（带角色）