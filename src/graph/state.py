import operator
from dataclasses import dataclass, field
from typing import Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


@dataclass
class GraphState:
    """
    Represents the state of our agent.

    Attributes:
    """

    messages: Annotated[List[AnyMessage], add_messages] = field(default_factory=list)
    agent_results: Annotated[list, operator.add] = field(default_factory=list)
    inter_messages: List[AnyMessage] = field(default_factory=list)
    execute_tool_count: int = field(default=0)


@dataclass
class GraphConfig:
    max_execute_tool: int = field(default=3)