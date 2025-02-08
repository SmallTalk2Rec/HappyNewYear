from langgraph.types import Command
from langgraph.graph import END
from pydantic import BaseModel, Field

from graph.state import GraphState, GraphConfig


class RecommendMovieNode:
    def __init__(self, llm, tools, system_template):
        self.llm_with_tools = llm.bind_tools(tools)
        self.system_message = {
            "role": "system",
            "content": system_template,
        }

    def __call__(self, state: GraphState, config: GraphConfig) -> GraphState:
        messages = [self.system_message] + state.inter_messages
        result = self.llm_with_tools.invoke(messages)

        if result.tool_calls:
            if state.execute_tool_count >= config["configurable"]["max_execute_tool"]:
                return Command(
                    update={
                        "agent_results": [
                            f"Tool execution limit reached. Please try again later."
                        ],
                        "execute_tool_count": 0,
                    },
                    goto="supervisor_node",
                )
            else:
                return Command(
                    update={
                        "inter_messages": state.inter_messages + [result],
                    },
                    goto="execute_tool",
                )
        else:
            return Command(
                update={
                    "agent_results": [
                        f"<RecommendMovieAgent>\n{result.content}\n</RecommendMovieAgent>"
                    ],
                    "execute_tool_count": 0,
                },
                goto="supervisor_node",
            )