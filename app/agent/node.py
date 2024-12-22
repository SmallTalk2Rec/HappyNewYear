import json
from langchain_core.messages import ToolMessage
from agent.state import AgentState
from agent.model import llm


class ChatBotNode:
    def __init__(self, tools):
        self.llm_with_tools = llm.bind_tools(tools)
    
    def __call__(self, state: AgentState) -> AgentState:
        return {"messages": [self.llm_with_tools.invoke(state.messages)]}
    

class ExecuteToolNode:
    def __init__(self, tools):
        self.tools_by_name = {tool.name: tool for tool in tools}
    
    def __call__(self, state: AgentState) -> AgentState:
        message = state.messages[-1]

        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=tool_result,
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}
