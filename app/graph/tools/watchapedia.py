import os
import json
import ast
from tqdm import tqdm
from typing import Type, Optional, List
from dotenv import load_dotenv
import pandas as pd
from pydantic import BaseModel, Field
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
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


class MovieRetrieverInput(BaseModel):
    sql_query: str = Field(
        description="SQL query to filter movies based on metadata. Must use valid SQLite syntax and 'movie' as table name. Query MUST return a list of MovieIDs using 'SELECT MovieID FROM movie WHERE...'. Any other SELECT fields will be ignored as only MovieID column is processed."
    )
    semantic_query: str = Field(
        description="Natural language query in korean for semantic search on movie synopses. Used to find movies with similar plot elements or themes."
    )


class MovieRetrieverTool(BaseTool):
    name: str = "movie_retriever"
    description: str = (
        """Tool for searching movie using both SQL and semantic search."""
    )
    args_schema: Type[BaseModel] = MovieRetrieverInput
    return_direct: bool = False

    sql_retriever: object
    chroma: object

    def __init__(self, uri_path, data_path):
        contexts_df = pd.read_csv(data_path)
        contexts_df = preprocess_data(contexts_df)

        # sql db 생성
        if not os.path.exists(uri_path.replace("sqlite:///", "")):
            engine = create_engine(uri_path)
            contexts_df.to_sql("movie", engine, if_exists="fail", index=False)
            engine.dispose()
        sql_db = SQLDatabase.from_uri(uri_path)
        sql_retriever = QuerySQLDataBaseTool(db=sql_db)

        # vector db 생성
        chroma = create_vector_db(contexts_df, persist_directory="./data/chroma")

        super().__init__(sql_retriever=sql_retriever, chroma=chroma)

    def _run(
        self,
        sql_query: str = None,
        semantic_query: str = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        response = self.sql_retriever.invoke({"query": sql_query})
        print("sql_query result: ", response)
        if response == "":
            return "[]"
        else:
            movie_ids = [item[0] for item in ast.literal_eval(response)]
        semantic_query = "" if semantic_query is None else semantic_query
        items = search_movies(self.chroma, movie_ids, semantic_query)
        context = json.dumps(
            [item["metadata"] for item in items], ensure_ascii=False, indent=4
        )
        return context

    async def _arun(
        self,
        sql_query: str = None,
        semantic_query: str = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ):
        return self._run(sql_query, semantic_query, run_manager)


def preprocess_data(contexts_df):
    """
    데이터 전처리
    """
    # 데이터 전처리
    contexts_df = contexts_df.dropna(subset=["Title"])

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
            if contexts_df[col].dtype in ["float64", "int64"]:
                contexts_df[col] = contexts_df[col].fillna(0)
            else:
                contexts_df[col] = contexts_df[col].fillna("")

    return contexts_df


def create_vector_db(
    contexts_df=None, persist_directory="./chroma_db", batch_size=40000
):
    """
    벡터 DB를 생성하거나 로드하는 함수
    - 이미 존재하면 로드
    - 존재하지 않으면 새로 생성
    """
    # OpenAI 임베딩 초기화
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # 벡터 DB가 이미 존재하는지 확인
    if os.path.exists(persist_directory):
        print("Loading existing vector DB...")
        return Chroma(
            persist_directory=persist_directory, embedding_function=embeddings
        )

    # contexts_df가 제공되지 않았는데 DB도 없는 경우
    if contexts_df is None:
        raise ValueError("contexts_df must be provided when creating new vector DB")

    print("Creating new vector DB...")

    # 배치 처리를 위한 준비
    total_rows = len(contexts_df)
    vectorstore = None

    for start_idx in range(0, total_rows, batch_size):
        end_idx = min(start_idx + batch_size, total_rows)
        batch_df = contexts_df.iloc[start_idx:end_idx]

        documents = []
        ids = []

        print(
            f"Processing batch {start_idx//batch_size + 1} of {(total_rows + batch_size - 1)//batch_size}"
        )

        for _, row in batch_df.iterrows():
            # 메타데이터 생성
            metadata = row.to_dict()
            metadata = {
                k: str(v) if isinstance(v, (int, float)) else v
                for k, v in metadata.items()
            }

            # Document 객체 생성
            doc = Document(page_content=str(row["Synopsis"]), metadata=metadata)

            documents.append(doc)
            ids.append(str(row["MovieID"]))

        # 첫 배치는 vectorstore 생성
        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=persist_directory,
                ids=ids,
            )
        else:
            # 이후 배치는 문서 추가
            vectorstore.add_documents(documents, ids=ids)

        # 각 배치 후 저장
        #    vectorstore.persist()
        print(f"Completed batch {start_idx//batch_size + 1}")

    print("Vector DB creation completed")
    return vectorstore


def search_movies(vectorstore, movie_ids, query, top_k=5):
    """
    movie_ids로 필터링 후 유사도 검색 수행
    """
    # movie_ids를 문자열로 변환
    movie_ids = [str(id) for id in movie_ids]

    # 필터 조건 생성
    filter = {"MovieID": {"$in": movie_ids}}

    # 검색 수행
    results = vectorstore.similarity_search_with_score(query, k=top_k, filter=filter)

    # 결과 정리
    search_results = []
    for doc, score in results:
        search_results.append(
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity": 1 - score,
            }
        )

    return search_results
