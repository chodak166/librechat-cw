import time
import asyncio
from datetime import datetime

from wfrun import BaseWorkflow

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ActiveParserChat import ActiveParserChat
from CodeSaverActiveParser import CodeSaverActiveParser

def get_random_string(length):
  letters = string.ascii_lowercase
  result_str = ''.join(random.choice(letters) for i in range(length))
  return result_str

class Workflow(BaseWorkflow):
  def __init__(self):
    pass

  async def response_stream_generator(self, input, history, options):
    session_id = ""
    if hasattr(options, 'conversation_id') and options.conversation_id is not None:
      session_id = options.conversation_id
    else:
      session_id = get_random_string(16)

    chat = ActiveParserChat()
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
