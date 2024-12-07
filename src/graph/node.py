import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from graph import prompt
from graph.tool import movie_retriever
from graph.state import GraphState
from graph.model import llm
from graph.utils import JSONParser


def get_movie(state: GraphState) -> GraphState:
    docs = movie_retriever.invoke(state["question"])
    context = ""
    for doc in docs:
        context += json.dumps(doc.metadata, indent=4) + "\n\n"
    return GraphState(context=context)


def get_answer(state: GraphState) -> GraphState:
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt.SYSTEM_TEMPLATE),
            ("user", prompt.USER_TEMPLATE),
        ]
    )
    chain = template | llm | JSONParser()
    response = chain.invoke(
        {
            "question": state["question"],
            "context": state["context"],
        }
    )
    return GraphState(answer=response["answer"])
