from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START

from graph.tools import MovieRetrieverTool
from graph.state import GraphState
from graph.node import SupervisorNode, RecommendMovieNode
from graph.prompt import SUPERVISOR_AGENT, RECOMMEND_MOVIE_AGENT

load_dotenv()


class ConversationLangGraph:
    def __init__(self):
        """Initialize the ConversationLangGraph object."""
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.workflow = StateGraph(GraphState)

        # Define the nodes
        self.workflow.add_node(
            "supervisor_node",
            SupervisorNode(llm=self.llm, system_template=SUPERVISOR_AGENT),
        )

        self.workflow.add_node(
            "recommend_movie_node",
            RecommendMovieNode(
                llm=self.llm,
                tools=[
                    MovieRetrieverTool(
                        movie_data_path="./data/241210/movie_info_watch.csv",
                        vectorstore_dir="./data/chroma",
                    )
                ],
                system_template=RECOMMEND_MOVIE_AGENT,
            ),
        )

        # Define edges
        self.workflow.add_edge(START, "supervisor_node")

        # Compile the workflow
        self.graph = self.workflow.compile()

    def get_graph(self):
        """Return the compiled graph instance."""
        return self.graph

    def run(self, message):
        """Run the graph with user message"""
        grapn_response = self.graph.invoke({"messages": str(message)})["messages"][
            -1
        ].content
        return grapn_response
