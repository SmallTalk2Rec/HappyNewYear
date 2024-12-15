from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START

from graph.tools import MovieRetrieverTool
from graph.state import GraphState
from graph.node import RecommendMovieNode
from graph.prompt import RECOMMEND_MOVIE

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node(
    "recommend_movie_node", 
    RecommendMovieNode(
        llm=llm, 
        tools=[
            MovieRetrieverTool(
                movie_data_path="./data/rotten_tomatoes_movie_df.csv", 
                vectorstore_dir="./data/chroma"
            )
        ],
        system_template=RECOMMEND_MOVIE
    )
)

workflow.add_edge(START, "recommend_movie_node")

# Compile the workflow
graph = workflow.compile()
