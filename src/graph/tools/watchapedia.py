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
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from sqlalchemy import create_engine


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
        description="SQL query to search movie information. Must be valid SQLite syntax and use 'movie' as table name. Query can include SELECT statements with various conditions (WHERE, ORDER BY, etc.) to filter and sort movie data. Returns movie details including title, genre, ratings, cast information, and more."
    )


class MovieRetrieverTool(BaseTool):
    name: str = "movie_retriever"
    description: str = """Tool for searching Korean movie database using SQL queries.

Usage:
- Execute queries with tool.invoke({"query": "YOUR_SQL_QUERY"})
- Use SQLite syntax with 'movie' table
- Filter/sort using WHERE, ORDER BY, etc.

Main fields:
- MovieID: Unique identifier
- Title
- Year
- Genre
- Country
- Runtime: e.g. '1시간 30분'
- Age: "전체"|"7세"|"12세"|"15세"|"청불"
- Avg_Rating: 0-5 scale
- N_Rating(만명): Ratings count in 10k
- N_Comments: Review count
"""

    args_schema: Type[BaseModel] = MovieRetrieverInput
    return_direct: bool = False

    db_tool: object

    def __init__(self, uri_path, data_path):
        if not os.path.exists(uri_path.replace("sqlite:///", "")):
            contexts_df = pd.read_csv(data_path)
            contexts_df = contexts_df.dropna(subset=['Title'])

            def func(x):
                if pd.isna(x):
                    return None
                x = x.strip("+\n")
                if pd.isna(x) or x == "None":
                    return None
                return float(x)
            
            contexts_df["N_Comments"] = contexts_df["N_Comments"].apply(func)        
            for col in contexts_df.columns:
                if col in contexts_df.columns:
                    if contexts_df[col].dtype in ['float64', 'int64']:
                        contexts_df[col] = contexts_df[col].fillna(0)
                    else:
                        contexts_df[col] = contexts_df[col].fillna('')

            engine = create_engine(uri_path)
            contexts_df.to_sql('movie', engine, if_exists='fail', index=False)
            engine.dispose()
        
        movie_db = SQLDatabase.from_uri(uri_path)
        db_tool = QuerySQLDataBaseTool(db=movie_db)
        
        super().__init__(db_tool=db_tool)

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None):
        context = self.db_tool.invoke({"query": query})
        return context

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ):
        return self._run(query, run_manager)

