from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START

from graph.tools import MovieRetrieverTool
from graph.state import GraphState
from graph.node import SupervisorNode, RecommendMovieNode
from graph.prompt import SUPERVISOR_AGENT, RECOMMEND_MOVIE_AGENT

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node(
    "supervisor_node",
    SupervisorNode(
        llm=llm,
        system_template=SUPERVISOR_AGENT
    )
)

workflow.add_node(
    "recommend_movie_node", 
    RecommendMovieNode(
        llm=llm, 
        tools=[
            MovieRetrieverTool(
                uri_path="sqlite:///data/movie_info_watch_sql.db", 
                data_path="./data/241228/movie_info_watch.csv"
            )
        ],
        system_template=RECOMMEND_MOVIE_AGENT
    )
)

workflow.add_edge(START, "supervisor_node")

# Compile the workflow
graph = workflow.compile()
