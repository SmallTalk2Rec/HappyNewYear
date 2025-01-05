import os
from dotenv import load_dotenv
from graph.builder import graph

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "smalltalk2rec"

query = " 추천해줘"

response = graph.invoke({"messages": [("human", query)]}, config={"configurable": {"max_execute_tool": 3}})
print(response)