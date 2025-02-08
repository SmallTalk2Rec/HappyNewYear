from pydantic import BaseModel, Field
from langgraph.types import Command
from langgraph.graph import END

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