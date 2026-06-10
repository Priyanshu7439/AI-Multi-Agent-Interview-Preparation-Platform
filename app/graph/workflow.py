from langgraph.graph import StateGraph, START, END
from app.graph.state import InterviewGraphState
from app.graph.nodes import WorkflowNodes

def route_mock_interview(state: InterviewGraphState) -> str:
    """Conditional router that determines whether to pause for candidate answers or proceed to evaluation."""
    questions = state.get("questions") or []
    answers = state.get("answers") or []
    
    if not questions:
        return "end"
        
    if len(answers) < len(questions):
        # Pause execution (exit graph) to wait for candidate response via API
        return "end"
    else:
        # All questions answered, proceed to evaluation
        return "evaluation"

def create_interview_workflow(nodes: WorkflowNodes):
    """Create and compile the StateGraph for the multi-agent interview preparation workflow."""
    workflow = StateGraph(InterviewGraphState)

    # 1. Add Nodes
    workflow.add_node("resume_analysis", nodes.resume_analysis_node)
    workflow.add_node("jd_analysis", nodes.jd_analysis_node)
    workflow.add_node("gap_analysis", nodes.gap_analysis_node)
    workflow.add_node("question_generation", nodes.question_generation_node)
    workflow.add_node("mock_interview", nodes.mock_interview_node)
    workflow.add_node("evaluation", nodes.evaluation_node)
    workflow.add_node("career_coaching", nodes.career_coaching_node)

    # 2. Add Edges (START -> Resume -> JD -> Gap -> Question -> Mock Interview)
    workflow.add_edge(START, "resume_analysis")
    workflow.add_edge("resume_analysis", "jd_analysis")
    workflow.add_edge("jd_analysis", "gap_analysis")
    workflow.add_edge("gap_analysis", "question_generation")
    workflow.add_edge("question_generation", "mock_interview")

    # 3. Add Conditional Edge from Mock Interview Node
    workflow.add_conditional_edges(
        "mock_interview",
        route_mock_interview,
        {
            "end": END,
            "evaluation": "evaluation"
        }
    )

    # 4. Add Final Edges
    workflow.add_edge("evaluation", "career_coaching")
    workflow.add_edge("career_coaching", END)

    # 5. Compile
    return workflow.compile()
