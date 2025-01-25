from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from langgraph.graph import END
from pydantic import BaseModel, Field

from graph.state import GraphState, GraphConfig


class Router(BaseModel):
    target: str = Field(
        description="The target of the message, either ‘user’ or 'RecommendMovieAgent'"
    )
    message: str = Field(description="The message to be sent to the target")


class SupervisorNode:
    def __init__(self, llm, system_template):
        self.llm = llm.with_structured_output(Router)
        self.system_message = {
            "role": "system",
            "content": system_template,
        }

    def __call__(self, state: GraphState, config: GraphConfig) -> GraphState:
        agent_results = "\n\n".join(state.agent_results)
        human_message = {
            "role": "human",
            "content": f"<user>\n{state.messages[-1].content}\n</user>\n\n{agent_results}",
        }
        messages = [self.system_message] + state.messages[:-1] + [human_message]
        response = self.llm.invoke(messages)

        if response.target == "RecommendMovieAgent":
            return Command(
                update={
                    "inter_messages": [
                        {
                            "role": "human",
                            "content": f"{agent_results}\n\n<user>\n{response.message}\n</user>",
                        }
                    ]
                },
                goto="recommend_movie_node",
            )
        elif response.target == "user":
            return Command(
                update={
                    "messages": [{"role": "assistant", "content": response.message}]
                },
                goto=END,
            )
        else:
            raise ValueError("Invalid target")


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
