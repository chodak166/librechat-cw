import asyncio
import json
import time
import random

from typing import Optional, List
from pydantic import Field
from starlette.responses import StreamingResponse, JSONResponse
from fastapi import FastAPI, HTTPException, Request
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

    async def parse_chat_request(self, request: Request) -> ChatCompletionRequest:
        headers = request.headers
        print(f"Headers: {headers}")

        body = await request.body()
        print(f"Body: {body.decode('utf-8')}")

        # Parse and print the request as a `ChatCompletionRequest` model
        chat_request = None
        try:
            data = json.loads(body)
            chat_request = ChatCompletionRequest(**data)
            print("Getting conversation id")
            if "Conversation-Id" not in headers:
                chat_request.conversation_id = self.random_string(10)
            else:
                chat_request.conversation_id = headers["Conversation-Id"]
                chat_request.remote_conversation_id = True

            print(f"Parsed Request: {chat_request}")
        except Exception as e:
            print(f"Failed to parse chat request: {e}")

        if not chat_request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        return chat_request

    async def _restream_response(self, response_stream, request):
        i = 0
        async for value in response_stream:
            i += 1
            chunk = {
                "id": "chatcmpl-" + str(i) + self.random_string(10),
                "object": "chat.completion.chunk",
                "created": time.time(),
                "model": request.model,
                "choices": [{"index": i, "finish_reason": "stop", "delta": {"content": value}}],
            }
            data = json.dumps(chunk)
            yield f"data: {data}\n\n"

        print("Writing end of stream")
        yield "data: [DONE]\n\n"

    async def async_stream_to_string(self, astream):
        result = ""
        async for chunk in astream:
            if chunk is not None:
                result += chunk
        return result

    async def chat_completions(self, request: Request):
        print("New request\n")

        # Print the headers
        chat_request = await self.parse_chat_request(request)
        workflow = self.workflow_manager.create_workflow("workflows/" + chat_request.model + ".py")

        print("Getting response stream")
        astream = await workflow.get_response_stream(chat_request.messages, chat_request)
        print("Got response stream")

        if chat_request.stream:
            print("Returning STREAM response")
            return StreamingResponse(
                self._restream_response(astream, chat_request), media_type="application/json"
            )

        response = await self.async_stream_to_string(astream)

        print("Returning STATIC response")
        return JSONResponse(content={
            "id": "0",
            "object": "chat.completion",
            "created": time.time(),
            "model": chat_request.model,
            "choices": [{"message": {"role": "assistant", "content": response}}],
        })

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

