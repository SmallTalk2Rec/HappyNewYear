from dotenv import load_dotenv
import pandas as pd
from langchain_chroma import Chroma

from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.document_loaders import DataFrameLoader
from langchain_openai import OpenAIEmbeddings
from graph.model import llm


load_dotenv()

metadata_field_info = [
    AttributeInfo(
        name="title",
        description="The title of the movie.",
        type="string",
    ),
    AttributeInfo(
        name="director",
        description="A list of the movie's directors.",
        type="list",
    ),
    AttributeInfo(
        name="screenwriter",
        description="A list of the movie's screenwriters.",
        type="list",
    ),
    AttributeInfo(
        name="plot",
        description="A short summary of the movie's plot.",
        type="string",
    ),
    AttributeInfo(
        name="rating",
        description="The average rating given to the movie. Range 0.0 ~ 5.0",
        type="float",
    ),
    AttributeInfo(
        name="rating_count",
        description="The total number of ratings the movie has received.",
        type="float",
    ),
    AttributeInfo(
        name="actors",
        description="A list of the movie's main actors.",
        type="list",
    ),
    AttributeInfo(
        name="genres",
        description="A list of the genres.",
        type="list",
    ),
    AttributeInfo(
        name="countries",
        description="A list of the countries where the movie was produced.",
        type="list",
    ),
    AttributeInfo(
        name="audience",
        description="Cumulative audience",
        type="float",
    ),
    AttributeInfo(
        name="running_time",
        description="The running time of the movie in minutes.",
        type="float",
    ),
    AttributeInfo(
        name="adult",
        description="A flag indicating whether the movie is for adults only.",
        type="float",
    ),
]
content_description = "plot and reviews of the movie"


contexts_df = pd.read_csv("./data/movies_sample_cleaned_chroma.csv")
loader = DataFrameLoader(contexts_df, page_content_column="plot_review")

vectorstore = Chroma.from_documents(
    loader.load(),
    # HuggingFaceEmbeddings(
    #     model_name="upskyy/bge-m3-korean", model_kwargs={"device": "cuda"}
    # ),
    OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory="./data/chroma",
)


movie_retriever = SelfQueryRetriever.from_llm(
    llm, vectorstore, content_description, metadata_field_info
)
