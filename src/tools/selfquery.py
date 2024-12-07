import json
from tqdm import tqdm
from typing import Type, Optional, List
from dotenv import load_dotenv
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.documents import Document
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

content_description = "Movie title, genre, director, and writer"

metadata_field_info = [
    AttributeInfo(
        name="audienceScore",
        description="Average rating from general audience. range 0 - 100",
        type="float",
    ),
    AttributeInfo(
        name="tomatoMeter",
        description="Average rating from critics. range 0 - 100",
        type="float",
    ),
    AttributeInfo(
        name="rating",
        description="Movie age rating (G, PG, PG-13, R, NC-17, TVY7, TVG, TVPG, TV14, TVMA).",
        type="string",
    ),
    AttributeInfo(
        name="ratingContents",
        description="Content leading to the rating classification",
        type="string",
    ),
    AttributeInfo(
        name="releaseDateTheater",
        description="The date the movie was released in theaters. (e.g. 2021-01-01)",
        type="string",
    ),
    AttributeInfo(
        name="releaseDateStreaming",
        description="The date the movie became available for streaming. (e.g. 2021-01-01)",
        type="string",
    ),
    AttributeInfo(
        name="runtimeMinutes",
        description="The duration of the movie in minutes",
        type="float",
    ),
    AttributeInfo(
        name="originalLanguage",
        description="The original language of the movie",
        type="string",
    ),
    AttributeInfo(
        name="boxOffice",
        description="The movie's total box office revenue. (e.g. $1.2M)",
        type="string",
    ),
    AttributeInfo(
        name="distributor",
        description="The company responsible for distributing the movie",
        type="string",
    ),
    AttributeInfo(
        name="soundMix",
        description="The audio format(s) used in the movie",
        type="string",
    ),
]


def process_in_batches(documents: List[Document], embeddings, batch_size: int = 40000):
   total_docs = len(documents)
   vectorstore = None
   
   # tqdm으로 진행률 표시
   progress_bar = tqdm(
       range(0, total_docs, batch_size),
       desc="Creating vector store",
       total=(total_docs + batch_size - 1) // batch_size
   )
   
   for i in progress_bar:
       batch = documents[i:min(i + batch_size, total_docs)]
       progress_bar.set_postfix({"batch": f"{i//batch_size + 1}", "docs": f"{len(batch)}"})
       
       if vectorstore is None:
           vectorstore = Chroma.from_documents(
               batch,
               embeddings,
               persist_directory="./data/chroma",
           )
       else:
           vectorstore.add_documents(batch)
   
   return vectorstore



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
        contexts_df['title_genre_director_writer'] = contexts_df['title_genre_director_writer'].fillna('')
        
        # 메타데이터 컬럼의 NaN 값 처리
        metadata_columns = [info.name for info in metadata_field_info]
        for col in metadata_columns:
            if col in contexts_df.columns:
                if contexts_df[col].dtype in ['float64', 'int64']:
                    contexts_df[col] = contexts_df[col].fillna(0)
                else:
                    contexts_df[col] = contexts_df[col].fillna('')

        # Document 생성
        print("Creating document loader...")
        loader = DataFrameLoader(contexts_df, page_content_column="title_genre_director_writer")
        documents = loader.load()

        print("Initializing embeddings...")
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vectorstore = process_in_batches(documents, embeddings)

        super().__init__(movie_retriever=SelfQueryRetriever.from_llm(
            llm, vectorstore, content_description, metadata_field_info
        ))

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

