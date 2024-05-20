from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from typing import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

import time

from workflows.lib.LangchainChatBase import LangchainChatBase

class ActiveParserChat(LangchainChatBase):

    def __init__(self, llm, prompt, max_parser_feedbacks = 3):
        super().__init__(llm, prompt)
        self.active_parsers = []
        self.max_parser_feedbacks = max_parser_feedbacks
        self.input_chain = prompt | llm | StrOutputParser()

    def add_active_parser(self, parser):
        self.active_parsers.append(parser)


    def stream(self, input, feedback_count = 0) -> Generator[str, None, None]:
        print("FEEDBACK COUNT: " + str(feedback_count), flush=True)
        if feedback_count >= self.max_parser_feedbacks:
            return

        print(self.chat_history, flush=True)
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

