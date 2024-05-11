from pydantic import BaseModel
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
