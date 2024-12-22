from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from langgraph.graph import END
from pydantic import BaseModel, Field

from graph.state import GraphState


class Router(BaseModel):
    target: str = Field(description="The target of the message, either ‘user’ or 'RecommendMovieAgent'")
    message: str = Field(description="The message to be sent to the target")


class SupervisorNode:
    def __init__(self, llm, system_template):
        self.llm = llm.with_structured_output(Router)
        self.system_message = [
            {
                "role": "system",
                "content": system_template,
            }
        ]
    
    def __call__(self, state: GraphState) -> GraphState:
        messages = self.system_message + state.messages + state.inter_messages
        response = self.llm.invoke(messages)

        if response.target == "RecommendMovieAgent":
            return Command(
                update={
                    "inter_messages": [
                        {
                            "role": "assistant",
                            "name": "SupervisorAgent",
                            "content": response.message
                        }
                    ]
                },
                goto="recommend_movie_node"
            )
        elif response.target == "user":
            return Command(
                update={
                    "messages": [
                        {
                            "role": "assistant",
                            "name": "SupervisorAgent",
                            "content": response.message
                        }
                    ]
                },
                goto=END
            )
        else:
            raise ValueError("Invalid target")
    


class RecommendMovieNode:
    def __init__(self, llm, tools, system_template):
        self.agent = create_react_agent(llm, tools=tools, state_modifier=system_template)
    
    def __call__(self, state: GraphState) -> GraphState:
        result = self.agent.invoke({"messages": state.inter_messages})
        return Command(
            update={
                "inter_messages": [
                    {
                        "role": "assistant",
                        "name": "RecommendMovieAgent",
                        "content": result["messages"][-1].content
                    }
                ]
            },
            goto="supervisor_node"
        )