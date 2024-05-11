import time
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


  async def response_stream_generator(self, history):
    last_message = history[-1].content if len(history) > 0 else ""
    text = "I'm just repeating after you: " + last_message
    # stream two characters at once
    chunks = [text[i:i+2] for i in range(0, len(text), 2)]
    for chunk in chunks:
      time.sleep(0.05)
      yield chunk

  async def get_response_stream(self, history, options):
    return self.response_stream_generator(history)
