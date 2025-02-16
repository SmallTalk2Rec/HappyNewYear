import json
from typing import Optional, List
from langgraph.types import Command
from langgraph.graph import END
from pydantic import BaseModel, Field

from graph.state import GraphState, GraphConfig


# USER_PROMPT = """<user_profile>
# {user_profile}
# </user_profile>

# Please update user profile by taking into account the new messages above:"""

USER_PROMPT = """<user_profile>
{user_profile}
</user_profile>

Please update the existing user profile based on previous conversations."""


class WatchedMovie(BaseModel):
    name: str = Field(description="The name of the movie")
    review: Optional[str] = Field(description="The review of the user", default=None)

class RecommendedMovie(BaseModel):
    name: str = Field(description="The name of the movie")
    reason: Optional[str] = Field(description="Reason for recommending the movie", default=None)


class UserProfile(BaseModel):
    name: str = Field(description="The name of the user")
    watched_movies: List[WatchedMovie] = Field(description="The movies the user said they watched")
    recommended_movies: List[RecommendedMovie] = Field(description="The movies recommended to the user")
    movie_preference: str = Field(description="The user's movie preference")


class UserProfilingNode:
    def __init__(self, llm):
        self.llm = llm.with_structured_output(UserProfile)
    
    def __call__(self, state: GraphState, config: GraphConfig) -> GraphState:
        user_profile = json.dumps(
            state.user_profile,
            indent=2,
            ensure_ascii=False
        )
        messages = state.messages + [{"role": "human", "content": USER_PROMPT.format(user_profile=user_profile)}]
        response = self.llm.invoke(messages).model_dump()

        return Command(
            goto=END,
            update={
                "user_profile": response
            }
        )