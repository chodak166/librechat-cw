from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from typing import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

import time

class LangchainChatBase:
    def __init__(self, llm, prompt):
        self.chat_history = []
        self._CHUNK_SLEEP = 0.1
        self._CHUNK_LEN = 16

        self.llm = llm
        self.prompt = prompt


    def _yield_text(self, text):
        chunks = [text[i:i+self._CHUNK_LEN] for i in range(0, len(text), self._CHUNK_LEN)]
        for chunk in chunks:
            time.sleep(self._CHUNK_SLEEP)
            yield chunk

    def add_history_message(self, role, content):
        if role.lower() == "assistant":
            self.chat_history.append(AIMessage(content=content))
        else:
            self.chat_history.append(HumanMessage(content=content))

    def stream(self, input) -> Generator[str, None, None]:

        chain = self.prompt | self.llm | StrOutputParser()
        stream = chain.stream({"input": input, "chat_history": self.chat_history})
        for chunk in stream:
            yield chunk



if __name__ == '__main__':

    llm = ChatGroq(
        temperature=1.0,
        model="llama3-8b-8192",
     )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful software developer. You write code modern and optimal code."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ]
    )

    chat = LangchainChatBase(llm, prompt)
    user_input = "Write a function that split string into a vector in C++17."
    stream = chat.stream(user_input)
    for chunk in stream:
        print(chunk, end="", flush=True)

