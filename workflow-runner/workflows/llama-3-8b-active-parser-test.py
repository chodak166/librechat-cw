import asyncio

import sys
import os

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from workflows.lib.ActiveParserChat import ActiveParserChat
from workflows.lib.parsers.SummaryActiveParser import SummaryActiveParser

BASE_MODEL = "llama3-8b-8192"

class Workflow:

  async def response_stream_generator(self, input, history):

    llm = ChatGroq(
        temperature=1.0,
        model=BASE_MODEL,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant. You follow human instructions strictly."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ]
    )

    chat = ActiveParserChat(llm, prompt, max_parser_feedbacks = 3)
    for item in history:
      chat.add_history_message(item.role, item.content)

    summaryParser = SummaryActiveParser()
    chat.add_active_parser(summaryParser)

    stream = chat.stream(input)
    for chunk in stream:
      await asyncio.sleep(0)
      yield chunk

  async def get_response_stream(self, history, options):
    input = history[-1].content
    history = history[:-1]
    return self.response_stream_generator(input, history)
