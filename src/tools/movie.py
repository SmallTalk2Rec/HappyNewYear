import os
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
from langchain.chains.query_constructor.base import StructuredQueryOutputParser
from langchain_community.document_loaders import DataFrameLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.query_constructors.chroma import ChromaTranslator
from langchain.chains.query_constructor.ir import StructuredQuery


load_dotenv()


def process_in_batches(documents: List[Document], embeddings, batch_size: int = 40000, vectorstore_dir: str = "./data/chroma"):
    if os.path.exists(vectorstore_dir):
        vectorstore = Chroma(embedding_function=embeddings, persist_directory=vectorstore_dir)
        return vectorstore
   
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
                persist_directory=vectorstore_dir,
            )
        else:
            vectorstore.add_documents(batch)

    return vectorstore



class MovieRetrieverInput(BaseModel):
    query: str = Field(
        description="Text string to search within movie contents (title, genre, director, writer). Should only contain search terms without any filtering conditions."
    )
    filter: Optional[str] = Field(
        description="""Optional logical condition statement for filtering movies. Must use the following format:
        - Comparison: comp(attr, val) where comp is one of: eq, ne, gt, gte, lt, lte
        - Logical operations: op(statement1, statement2, ...) where op is one of: and, or
        - Date format must be YYYY-MM-DD
        - Use 'NO_FILTER' if no filtering is needed
        Example: 'and(gt("audienceScore", 80), lt("releaseDateTheater", "2024-01-01"))'"""
    )


class MovieRetrieverTool(BaseTool):
    name: str = "movie_retriever"
    description: str = """Tool for searching movie with the following information:
    - Movie title
    - Genre
    - Director
    - Writer
    - audienceScore: Average rating from general audience (0-100)
    - tomatoMeter: Average rating from critics (0-100)
    - rating: Movie age rating (G, PG, PG-13, R, NC-17, TVY7, TVG, TVPG, TV14, TVMA)
    - ratingContents: Content leading to the rating classification
    - releaseDateTheater: Theater release date (YYYY-MM-DD)
    - releaseDateStreaming: Streaming availability date (YYYY-MM-DD)
    - runtimeMinutes: Movie duration in minutes
    - boxOffice: Total box office revenue (e.g. $1.2M)
    - originalLanguage: Original language of the movie
    - distributor: Distribution company
    - soundMix: Audio format(s) used

    Use comparison operators (eq, ne, gt, gte, lt, lte) and logical operators (and, or) for filtering.
    Returns relevant movie data matching the specified criteria."""
    args_schema: Type[BaseModel] = MovieRetrieverInput
    return_direct: bool = False

    filter_parser: object
    structured_query_translator: object
    vectorstore: object

    def __init__(self, movie_data_path: str, vectorstore_dir: str):
        contexts_df = pd.read_csv(movie_data_path)
        contexts_df = contexts_df.dropna(subset=['title'])
        
        for col in contexts_df.columns:
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
        vectorstore = process_in_batches(documents, embeddings, batch_size=40000, vectorstore_dir=vectorstore_dir)

        filter_parser = StructuredQueryOutputParser.from_components()
        structured_query_translator = ChromaTranslator()
        super().__init__(vectorstore=vectorstore, filter_parser=filter_parser, structured_query_translator=structured_query_translator)

    def _run(self, query: str, filter: str, run_manager: Optional[CallbackManagerForToolRun] = None):
        structured_query = StructuredQuery(query=query, filter=self.filter_parser.ast_parse(filter), limit=None)

        new_query, search_kwargs = self.structured_query_translator.visit_structured_query(structured_query)
        docs = self.vectorstore.search(new_query, "similarity", **search_kwargs)
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

