from langgraph.graph import END, StateGraph

from graph.state import GraphState
from graph.node import get_movie, get_answer

workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("get_movie", get_movie)
workflow.add_node("get_answer", get_answer)

# Define the edges
workflow.add_edge("get_movie", "get_answer")
workflow.add_edge("get_answer", END)

# Define the start node
workflow.set_entry_point("get_movie")

# Compile the workflow
pipeline = workflow.compile()
