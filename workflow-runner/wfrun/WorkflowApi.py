import asyncio
import json
import time
import random

from typing import Optional, List
from pydantic import Field
from starlette.responses import StreamingResponse
from fastapi import FastAPI, HTTPException
from.WorkflowManager import WorkflowManager
from.wftypes import ChatCompletionRequest, Message

class WorkflowApi:
    def __init__(self):
        self.app = FastAPI(title="OpenAI-compatible API")
        self.app.add_event_handler("startup", self.on_startup)
        self.app.add_event_handler("shutdown", self.on_shutdown)
        self.app.add_api_route("/chat/completions", self.chat_completions, methods=["POST"])
        self.app.add_api_route("/models", self.models, methods=["GET"])
        self.workflow_manager = WorkflowManager("workflows")

    async def on_startup(self):
        print("Initializing...")

    async def on_shutdown(self):
        print("Application is shutting down. Cleaning up resources.")

    def random_string(self, length):
        letters = "abcdefghijklmnopqrstuvwxyz"
        return ''.join(random.choice(letters) for i in range(length))

    async def _restream_response(self, response_stream, request):
        i = 0
        async for value in response_stream:
            print("Restreaming value:")
            print(value)
            i += 1
            chunk = {
                "id": "chatcmpl-" + str(i) + self.random_string(10),
                "object": "chat.completion.chunk",
                "created": time.time(),
                "model": request.model,
                "choices": [{"index": i, "finish_reason": "stop", "delta": {"content": value}}],
            }
            data = json.dumps(chunk)
            print("Writing: " + data)
            yield f"data: {data}\n\n"
            await asyncio.sleep(0.1)

        print("Writing end of stream")
        yield "data: [DONE]\n\n"

    async def chat_completions(self, request: ChatCompletionRequest):
        print("New request\n")
        print(request)

        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        if request.stream:
            workflow = self.workflow_manager.create_workflow("workflows/" + request.model + ".py")
            stream = await workflow.get_response_stream(request.messages, request)
            return StreamingResponse(
                self._restream_response(stream, request), media_type="application/json"
            )

        return {
            "id": "1337",
            "object": "chat.completion",
            "created": time.time(),
            "model": request.model,
            "choices": [{"message": Message(role="assistant", content="DUMMY RESPONSE")}],
        }

    async def models(self):
        print("New MODELS request\n")
        result = {
            "object": "list",
            "data": []
        }
        workflows = self.workflow_manager.list_workflows()
        for path, name in workflows:
            entry = {
                "id": name,
                "object": "model",
                "owned_by": "unknown",
            }
            result["data"].append(entry)
        return result

