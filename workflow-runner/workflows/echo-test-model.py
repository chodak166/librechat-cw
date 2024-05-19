import time
import asyncio
from datetime import datetime

from wfrun import BaseWorkflow

class Workflow(BaseWorkflow):
  def __init__(self):
    self.config = {
      "description": "This is a test workflow",
      "model": __file__.split('/')[-1].split('.')[0],
      "options": {
        "temperature": 0.7,
        "max_tokens": 256
      }
    }


  async def response_stream_generator(self, history, options):
    last_message = history[-1].content if len(history) > 0 else ""
    text = "Hi! I'm just repeating after you: " + last_message

    if hasattr(options, 'conversation_id') and options.conversation_id:
      text += "\n\nConversation ID: " + options.conversation_id

    if hasattr(options, 'remote_conversation_id'):
      if options.remote_conversation_id:
        text += "\n\nThis is true conversation ID."
      else:
        text += "\n\nThis is false conversation ID, please update client app."

    # stream two characters at once
    chunks = [text[i:i+2] for i in range(0, len(text), 2)]
    for chunk in chunks:
      await asyncio.sleep(0.1)
      yield chunk

  async def get_response_stream(self, history, options):
    return self.response_stream_generator(history, options)
