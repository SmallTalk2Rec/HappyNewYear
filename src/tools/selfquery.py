import json
from typing import Type, Optional
from dotenv import load_dotenv
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_chroma import Chroma
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.document_loaders import DataFrameLoader
from langchain_openai import OpenAIEmbeddings
from agent.model import llm


load_dotenv()

content_description = "plot and reviews of the movie"

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

class SelfQueryInput(BaseModel):
    query: str = Field(description="The query to search for movies.")


class SelfQueryTool(BaseTool):
    name: str = "movie_retriever"
    description: str = "A tool to retrieve movies based on a query."
    args_schema: Type[BaseModel] = SelfQueryInput
    return_direct: bool = False

    movie_retriever: object

    def __init__(self, movie_data_path: str):
        contexts_df = pd.read_csv(movie_data_path)
        loader = DataFrameLoader(contexts_df, page_content_column="plot_review")
        vectorstore = Chroma.from_documents(
            loader.load(),
            OpenAIEmbeddings(model="text-embedding-3-small"),
            persist_directory="./data/chroma",
        )
        super().__init__(movie_retriever=SelfQueryRetriever.from_llm(
            llm, vectorstore, content_description, metadata_field_info
        ))
        # self.movie_retriever = SelfQueryRetriever.from_llm(
        #     llm, vectorstore, content_description, metadata_field_info
        # )

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None):
        docs = self.movie_retriever.invoke(query)
        context = ""
        for doc in docs:
            context += json.dumps(doc.metadata, indent=4) + "\n\n"
        return context

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ):
        return self._run(query, run_manager)

