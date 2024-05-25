import time
import asyncio
from datetime import datetime

import sys
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from workflows.lib.ActiveParserChat import ActiveParserChat
from workflows.lib.parsers.LiveCodeActiveParser import LiveCodeActiveParser

def get_random_string(length):
  letters = string.ascii_lowercase
  result_str = ''.join(random.choice(letters) for i in range(length))
  return result_str

BASE_MODEL = "deepseek-coder"
MAX_FEEDBACKS = 3

class Workflow:

  async def response_stream_generator(self, input, history, options):
    session_id = self.get_session_id(options)

    llm = ChatOpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com/",
        model=BASE_MODEL,
        temperature=0.8,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are a helpful assistant. You write texts only between [<tag>] and [</tag>] tags."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", """Follow the instruction after INSTRUCTION tag.
Write response in this format:
```
[<response>]

[<file_path>]./file/path.extension[</file_path>]
[<code>]
source code
[</code>]
[<execute>]false[</execute>]
[<explanation>]
explanation
[</explanation>]

[<file_path>]./script_name.sh[</file_path>]
[<code>]
commands
[</code>]
[<execute>]true[</execute>]
[<explanation>]
explanation
[</explanation>]

[</response>]
```
INSTRUCTION: {input}""")
        ]
    )

    chat = ActiveParserChat(llm, prompt)
    for item in history:
      chat.add_history_message(item.role, item.content)

    p = LiveCodeActiveParser( output_dir="/app/ai-workspace/" + session_id, session_id=session_id, enable_execution=False, max_parser_feedbacks=MAX_FEEDBACKS)
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