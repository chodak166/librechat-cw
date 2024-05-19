from pydantic import BaseModel, Field
from typing import Optional, List

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "echo-test-model"
    messages: List[Message]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    stream: Optional[bool] = False
    conversation_id: Optional[str] = Field(default=None, alias="conversation_id")
    remote_conversation_id: Optional[bool] = Field(default=None, alias="remote_conversation_id")

