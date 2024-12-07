import re
import json
from langchain_core.messages import AIMessage
from langchain_core.output_parsers.string import StrOutputParser


class JSONParser(StrOutputParser):
    def __init__(self):
        super().__init__()

    def parse(self, ai_message: AIMessage):
        text = super().parse(ai_message)
        return json.loads(text)


