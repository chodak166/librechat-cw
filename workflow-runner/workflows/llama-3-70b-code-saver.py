import time
import asyncio
from datetime import datetime

import sys
import os

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from workflows.lib.ActiveParserChat import ActiveParserChat
from workflows.lib.parsers.CodeSaverActiveParser import CodeSaverActiveParser

def get_random_string(length):
  letters = string.ascii_lowercase
  result_str = ''.join(random.choice(letters) for i in range(length))
  return result_str

BASE_MODEL = "llama3-70b-8192"

class Workflow:

  async def response_stream_generator(self, input, history, options):
    session_id = self.get_session_id(options)

    llm = ChatGroq(
        temperature=0.0,
        model=BASE_MODEL,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are a helpful assistant.
            You follow human instructions strictly.
            You always write file names just before code blocks when writing code.
            You write shell commands in single sh code block."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ]
    )

    chat = ActiveParserChat(llm, prompt)
    for item in history:
      chat.add_history_message(item.role, item.content)

    p = CodeSaverActiveParser("/app/ai-workspace/" + session_id, session_id)
    chat.add_active_parser(p)

    stream = chat.stream(input)
    for chunk in stream:
      await asyncio.sleep(0)
      yield chunk

  async def get_response_stream(self, history, options):
    input = history[-1].content
    history = history[:-1]
    return self.response_stream_generator(input, history, options)

  def get_session_id(self, options):
    session_id = None
    if hasattr(options, 'conversation_id') and options.conversation_id is not None:
      session_id = options.conversation_id
    else:
      session_id = get_random_string(16)

    return session_id