from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from typing import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

import time

class ActiveParserChat:
    def __init__(self):
        self.chat_history = []
        self._CHUNK_SLEEP = 0.1
        self._CHUNK_LEN = 16
        self.active_parsers = []
        self.max_parser_feedbacks = 3

        llm = ChatGroq(
            temperature=1.0,
            model="llama3-8b-8192",
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant. You follow human instructions strictly."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ]
        )

        parser = StrOutputParser()

        # Create LLM Chain
        self.input_chain = prompt | llm | parser

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

    def add_active_parser(self, parser):
        self.active_parsers.append(parser)


    def stream(self, input, feedback_count = 0) -> Generator[str, None, None]:
        print("FEEDBACK COUNT: " + str(feedback_count), flush=True)
        if feedback_count >= self.max_parser_feedbacks:
            return

        response = ""
        stream = self.input_chain.stream({"input": input, "chat_history": self.chat_history})
        for chunk in stream:
            yield chunk
            response += chunk

        self.add_history_message("assistant", response)

        for parser in self.active_parsers:
            action = parser.parse(response, feedback_count)
            if action.info is not None:
                yield action.info

            if action.feedback is not None:
                print("Got feedback from parser", flush=True)
                yield from self.stream(action.feedback, feedback_count + 1)


if __name__ == '__main__':

    chat = ActiveParserChat()
    user_input = "Write a function that split string into a vector in C++17."
    stream = chat.stream(user_input)
    for chunk in stream:
        print(chunk, end="", flush=True)
