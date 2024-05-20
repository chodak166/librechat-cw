from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from typing import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

import asyncio

from workflows.lib.LangchainChatBase import LangchainChatBase

class CodeReviewMultiChat(LangchainChatBase):

    def __init__(self, name, llm, prompt):
        super().__init__(llm, prompt)
        self.name = name
        self.reviewers = [] # name, llm, prompt

    def add_reviewer(self, name, llm, prompt):
        self.reviewers.append((name, llm, prompt))

    def stream(self, input) -> Generator[str, None, None]:
        self.responses = []
        response_future = None

        with ThreadPoolExecutor() as executor:
            intro = self._get_intro_text()
            response_future = executor.submit(self._get_response_text, input)

            yield from self._yield_text(intro['intro'])

            response = response_future.result()

            self.responses.append(response)

            parser = StrOutputParser()
            i = 0
            for name, llm, prompt in self.reviewers:
                if i == len(self.reviewers) - 1:
                    yield from self._yield_text(intro['wait_messages'][i])
                    yield "\n\n---\n\n"
                    review_chain = prompt | llm | parser
                    stream = review_chain.stream({"input": response})
                    final_response = ""
                    for chunk in stream:
                        yield chunk
                        final_response += chunk
                    self.responses.append(final_response)
                else:
                    yield "\n\n"
                    response_future = executor.submit(self._get_review_text, llm, prompt, parser, response)
                    yield from self._yield_text(intro['wait_messages'][i])
                    response = response_future.result()
                    self.responses.append(response)

                i += 1

        yield "\n\n"

    def _get_intro_text(self):
        intro = {
            "intro": "Your question is now being answered by " + self.name + "...\n",
            "wait_messages": []
        }
        for name, llm, prompt in self.reviewers:
            intro['wait_messages'].append(f"Solution is now being reviewed by {name}.\n")
        return intro

    def _get_response_text(self, input):
        chain = self.prompt | self.llm | StrOutputParser()
        response = chain.invoke({"input": input, "chat_history": self.chat_history})
        response = response.replace("ANSWER:", "")
        return response

    def _get_review_text(self, llm, prompt, parser, input):
        review_chain = prompt | llm | parser
        response = review_chain.invoke({"input": input})
        response = response.replace("ANSWER:", "")
        return response
