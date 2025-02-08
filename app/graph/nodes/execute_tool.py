from langgraph.types import Command
from langgraph.graph import END
from pydantic import BaseModel, Field

from graph.state import GraphState, GraphConfig


class ExecuteToolNode:
    def __init__(self, tools):
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, state: GraphState):
        outputs = []

        for tool_call in state.inter_messages[-1].tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )

            outputs.append(
                {
                    "role": "tool",
                    "name": tool_call["name"],
                    "content": tool_result,
                    "tool_call_id": tool_call["id"],
                }
            )

        return Command(
            update={
                "inter_messages": state.inter_messages + outputs,
                "execute_tool_count": state.execute_tool_count + 1,
            },
            goto="recommend_movie_node",
        )