from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from langgraph.graph import END
from langchain_core.messages import AIMessage

from graph.state import GraphState


class RecommendMovieNode:
    def __init__(self, llm, tools, system_template):
        self.agent = create_react_agent(llm, tools=tools, state_modifier=system_template)
    
    def __call__(self, state: GraphState) -> GraphState:
        result = self.agent.invoke(state)
        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=result["messages"][-1].content,
                    )
                ]
            },
            goto=END
        )