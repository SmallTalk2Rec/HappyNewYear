import operator
from dataclasses import dataclass, field
from typing import Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


HUMAN_MESSAGE_N = 5

def latest_message(existing: list, update: list):
    messages = existing + update

    human_count = 0
    first_keep_index = 0
    for i in range(len(messages) - 1, -1, -1):
        if messages[i]["role"] == "human":
            human_count += 1
            if human_count >= HUMAN_MESSAGE_N:
                first_keep_index = i
                break
    return messages[first_keep_index:]


@dataclass
class GraphState:
    """
    Represents the state of our agent.

    Attributes:
    """

    messages: Annotated[List[AnyMessage], latest_message] = field(default_factory=list)
    agent_results: list = field(default_factory=list)
    inter_messages: List[AnyMessage] = field(default_factory=list)
    execute_tool_count: int = field(default=0)

    user_profile: dict = field(
        default_factory=lambda: {
            "name": "",
            "watched_movies": [],
            "recommended_movies": [],
            "movie_preference": ""
        }
    )


@dataclass
class GraphConfig:
    max_execute_tool: int = field(default=3)
