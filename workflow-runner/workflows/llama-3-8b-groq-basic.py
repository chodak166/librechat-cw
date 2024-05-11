from groq import AsyncGroq
from datetime import datetime
from omniask import BaseWorkflow
import os
import asyncio

class Workflow(BaseWorkflow):
  def __init__(self):
    self.config = {
      "description": "llama3-8b from groq.com",
      "api_base": "https://api.groq.com/openai/v1",
      "system": "You are a helpful assistant. You always thank the user at the end of your response.",
      "options": {
        "model": "llama3-8b-8192",
        "temperature": 0.3,
        "max_tokens": 128,
        "top_p": 0.05
      }
    }
    self.client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

  async def response_stream_generator(self, stream):
      async for chunk in stream:
          yield chunk.choices[0].delta.content

  async def get_response_stream(self, history, options):
      print("CALL: get_response_stream")
      print(history)

      opt = self.config["options"]
      stream = await self.client.chat.completions.create(
          model=opt["model"],
          temperature=opt["temperature"],
          top_p=opt["top_p"],
          max_tokens=opt["max_tokens"],
          messages=history,
          stream=True
      )
      return self.response_stream_generator(stream)
