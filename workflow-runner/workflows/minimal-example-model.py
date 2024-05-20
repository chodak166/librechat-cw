import asyncio

class Workflow():

  async def response_stream_generator(self, history, options):
    chunks = ["Hi! ", "This ", "is ", "a ", "test!\n"]

    for chunk in chunks:
      await asyncio.sleep(0.2)
      yield chunk

  async def get_response_stream(self, history, options):
    return self.response_stream_generator(history, options)
