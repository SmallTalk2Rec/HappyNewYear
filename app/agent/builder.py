from langgraph.graph import START, END, StateGraph

from agent.state import AgentState
from agent.node import ChatBotNode, ExecuteToolNode
from agent.route import route_tools
from tools import toolkits

workflow = StateGraph(AgentState)

# Define the nodes
workflow.add_node("chatbot", ChatBotNode(tools=toolkits))
workflow.add_node("execute_tool", ExecuteToolNode(tools=toolkits))

# Define the edges
workflow.add_edge(START, "chatbot")
workflow.add_conditional_edges(
    "chatbot",
    route_tools,
    {
        "execute_tool": "execute_tool",
        END: END,
    },
)
workflow.add_edge("execute_tool", "chatbot")

# Compile the workflow
graph = workflow.compile()
