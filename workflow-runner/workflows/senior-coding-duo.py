import asyncio
import sys
import os

# from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


from workflows.lib.CodeReviewMultiChat import CodeReviewMultiChat

BASE_MODEL = "openai/gpt-4o"
REVIEWER_MODEL = "anthropic/claude-3-opus"

class Workflow:

  async def response_stream_generator(self, input, history):

    llm = ChatOpenAI(
        api_key=os.environ["OPENROUTER_KEY"],
        base_url="https://openrouter.ai/api/v1",
        model=BASE_MODEL,
        temperature=1.2,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a senior software developer. You follow instructions carefully. You write clean, highly optimal code."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ]
    )

    chat = CodeReviewMultiChat("GPT-4o Senior Coder",llm, prompt)
    self.add_reviewers(chat)

    for item in history:
      chat.add_history_message(item.role, item.content)

    stream = chat.stream(input)
    for chunk in stream:
      await asyncio.sleep(0)  # yield control back to the event loop
      yield chunk

  def add_reviewers(self, chat):
    name1 = "Claude 3 Opus Senior Coder"
    llm1 = ChatOpenAI(
        api_key=os.environ["OPENROUTER_KEY"],
        base_url="https://openrouter.ai/api/v1",
        temperature=0.2,
        model=REVIEWER_MODEL,
    )

    prompt1 = ChatPromptTemplate.from_messages(
      [
          ("system", """You are a senior coding answer reviewer. You follow humans instructions strictly.
            You optimize, fix and refactor provided answers with source code. Your code is modern and highly optimal.
            You follow SOLID principles and good practices. You do not make comments or notes on the answer."""),
          ("human", "Please refactor all code blocks in the ANSWER below. Repeat the whole ANSWER as it is, but update code blocks. Start with 'ANSWER:'. \n\nANSWER:\n\n{input}\n")
      ]
    )

    chat.add_reviewer(name1, llm1, prompt1)
    # chat.add_reviewer(name1, llm1, prompt1)

  async def get_response_stream(self, history, options):
    input = history[-1].content
    history = history[:-1]
    return self.response_stream_generator(input, history)
