"""LangGraph workflow definition.

Defines the state graph with three nodes: extractor -> analyzer -> advisor
"""

from langgraph.graph import StateGraph, END
from workflow.state import AgentState
from workflow.nodes import extractor_node, analyzer_node, advisor_node


def build_workflow():
    """Build and compile the hiring agent workflow."""

    # Define the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("extractor", extractor_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("advisor", advisor_node)

    # Define edges: extractor -> analyzer -> advisor -> END
    workflow.add_edge("extractor", "analyzer")
    workflow.add_edge("analyzer", "advisor")
    workflow.add_edge("advisor", END)

    # Set entry point
    workflow.set_entry_point("extractor")

    return workflow.compile()


def run_workflow(input_text: str, input_type: str = "candidate", jd_text: str = None) -> dict:
    """Run the complete workflow and return the final output.

    Args:
        input_text: Raw text input (resume or project document)
        input_type: "candidate" or "project"
        jd_text: Optional job description for candidate matching

    Returns:
        Final output dict with extracted_data, analysis, and recommendation
    """
    from langgraph.checkpoint.memory import MemorySaver

    # Initialize state
    initial_state = AgentState(
        input_text=input_text,
        input_type=input_type,
        jd_text=jd_text
    )

    # Build and run workflow
    app = build_workflow()

    # Run with memory checkpoint for debugging
    config = {"configurable": {"thread_id": "hiring-agent"}}
    result = app.invoke(initial_state, config=config)

    return result.final_output or result.model_dump() if hasattr(result, 'final_output') else result