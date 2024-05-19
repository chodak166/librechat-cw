import time
import asyncio
from datetime import datetime

from wfrun import BaseWorkflow

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ActiveParserChat import ActiveParserChat
from SummaryActiveParser import SummaryActiveParser

class Workflow(BaseWorkflow):
  def __init__(self):
    pass

  async def response_stream_generator(self, input, history):
    chat = ActiveParserChat()
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
