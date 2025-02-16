import json
from pydantic import BaseModel, Field
from langgraph.types import Command
from langgraph.graph import END

from graph.state import GraphState, GraphConfig


SYSTEM_PROMPT = """You are a coordinator who directly interacts with users to manage the movie recommendation service. 
Your main responsibilities are as follows:

1. Collecting User Preference Information:
- For new users, you must collect the following information:
  - Preferred genres
  - Favorite directors or actors
  - Recently enjoyed movies
  - Preferred era (whether they prefer recent releases)
  - Preferred countries of origin for movies

2. Assessing User Status:
- Review the user profile and recent conversation history to determine if the user’s preference information is sufficient.
- If the information is insufficient, supplement it by asking additional questions; if it is sufficient, forward the user’s preference information to the RecommendMovieAgent.

3. Delivering Recommendations:
- Present recommendations received from the RecommendMovieAgent in a user-friendly manner
- Collect user feedback on recommended movies to incorporate into future recommendations

All conversations should maintain a friendly and natural tone while efficiently gathering necessary information.
"""


class Router(BaseModel):
    target: str = Field(
        description="The target of the message, either ‘user’ or 'RecommendMovieAgent'"
    )
    message: str = Field(description="The message to be sent to the target")


class SupervisorNode:
    def __init__(self, llm):
        self.llm = llm.with_structured_output(Router)
        self.system_message = {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }

    def __call__(self, state: GraphState, config: GraphConfig) -> GraphState:
        agent_results = "\n\n".join(state.agent_results)
        user_profile = json.dumps(
            state.user_profile,
            indent=2,
            ensure_ascii=False
        )
        human_message = {
            "role": "human",
            "content": f"<user_profile>\n{user_profile}\n<user_profile>\n\n<user_message>\n{state.messages[-1]['content']}\n</user_message>\n\n{agent_results}",
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
                    "messages": [{"role": "assistant", "content": response.message}],
                    "agent_results": [],
                },
                goto="user_profiling_node",
            )
        else:
            raise ValueError("Invalid target")