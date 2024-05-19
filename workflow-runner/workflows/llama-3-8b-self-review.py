import time
import asyncio
from datetime import datetime

from wfrun import BaseWorkflow

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from MultiChatChan_llama3_8b_selfreview import MultiChatChain

class Workflow(BaseWorkflow):
  def __init__(self):
    print("INIT")
    self.config = {
      "description": "Llama 3 8B self-reviewing multiple times",
      "model": "llama-3-8b multiplied"
    }

  async def response_stream_generator(self, input, history):
    chat = MultiChatChain()
    for item in history:
      chat.add_history_message(item.role, item.content)

    stream = chat.stream(input)
    for chunk in stream:
       # Yield control back to the event loop so that
       # the synchronous generator does not block other tasks
      await asyncio.sleep(0)
      yield chunk

  async def get_response_stream(self, history, options):
    input = history[-1].content
    history = history[:-1]
    return self.response_stream_generator(input, history)
