import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, START
from langfuse.callback import CallbackHandler

from graph.tools import MovieRetrieverTool
from graph.state import GraphState
from graph.node import SupervisorNode, RecommendMovieNode, ExecuteToolNode
from graph.prompt import SUPERVISOR_AGENT, RECOMMEND_MOVIE_AGENT

load_dotenv()


class ConversationLangGraph:
    def __init__(self):
        """Initialize the ConversationLangGraph object."""
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        checkpointer = PostgresSaver(
            ConnectionPool(
                conninfo=os.environ["POSTGRES_CHECKPOINT_URI"],
                max_size=10,
                kwargs={
                    "autocommit": True,
                    "prepare_threshold": 0,
                }
            )
        )
        checkpointer.setup()
        self.workflow = StateGraph(GraphState)

        self.tools = [
            MovieRetrieverTool(
                uri_path="sqlite:///data/movie_info_watch_sql.db",
                data_path="./data/241228/movie_info_watch.csv",
            )
        ]

        # Define the nodes
        self.workflow.add_node(
            "supervisor_node",
            SupervisorNode(llm=self.llm, system_template=SUPERVISOR_AGENT),
        )

        self.workflow.add_node(
            "recommend_movie_node",
            RecommendMovieNode(
                llm=self.llm,
                tools=self.tools,
                system_template=RECOMMEND_MOVIE_AGENT,
            ),
        )

        self.workflow.add_node("execute_tool", ExecuteToolNode(tools=self.tools))

        # Define edges
        self.workflow.add_edge(START, "supervisor_node")

        # Compile the workflow
        self.graph = self.workflow.compile(checkpointer=checkpointer)

    def get_graph(self):
        """Return the compiled graph instance."""
        return self.graph

    def run(self, message, user_id):
        """Run the graph with user message"""
        lanfuse_handler = CallbackHandler(
            user_id=user_id,
        )
        config = {
            "configurable": {
                "thread_id": user_id,
                "max_execute_tool": 3
            },
            "callbacks": [lanfuse_handler]
        }
        grapn_response = self.graph.invoke(
            {"messages": message},
            config=config,
        )["messages"][-1].content
        return grapn_response
