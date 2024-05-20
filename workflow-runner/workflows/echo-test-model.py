import time
import asyncio
from datetime import datetime

class Workflow():

  async def response_stream_generator(self, history, options):
    last_message = history[-1].content if len(history) > 0 else ""
    text = "Hi! I'm just repeating after you: " + last_message
    text += self.get_conversation_id_info(options)
    yield text

  def get_conversation_id_info(self, options):
    text = ""
    if hasattr(options, 'conversation_id') and options.conversation_id:
      text += "\n\nConversation ID: " + options.conversation_id

    if hasattr(options, 'remote_conversation_id'):
      if options.remote_conversation_id:
        text += "\n\nThis is true conversation ID."
      else:
        text += "\n\nThis is false conversation ID, please update client app."
    return text

  async def get_response_stream(self, history, options):
    return self.response_stream_generator(history, options)
