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
    inter_messages: Annotated[List[AnyMessage], add_messages] = field(default_factory=list)
