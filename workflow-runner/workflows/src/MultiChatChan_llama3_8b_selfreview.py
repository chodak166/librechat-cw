from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from typing import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

import time

class MultiChatChain:
    def __init__(self):
        self.chat_history = []
        self.responses = []
        self.number_of_reviews = 3
        self._CHUNK_SLEEP = 0.1
        self._CHUNK_LEN = 16

        llm0 = ChatGroq(
            temperature=1.0,
            model="llama3-8b-8192",
        )

        llm1 = ChatGroq(
            temperature=1.2,
            model="llama3-8b-8192",
        )

        llm2 = ChatGroq(
            temperature=0.2,
            model="llama3-8b-8192",
        )

        prompt0 = ChatPromptTemplate.from_messages(
            [
                ("system", """You are a helpful assistant. You only output JSON code."""),
                ("human", """Please write JSON code matching this format and fill the fields:
                 {{
                 "intro": "<Inform the user that his question is now being answered by multiple AI models and ask him to wait for a while>",
                 "progress_answer": "<inform user that the answer is ready but it is being reviewed>",
                 "wait_messages": [
                 <three messages asking user to wait a bit more>
                 ]
                 }}
                 """)
            ]
        )

        prompt1 = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful software developer. You write code in a single code block."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ]
        )

        prompt2 = ChatPromptTemplate.from_messages(
            [
                ("system", """You are a senior coding answer reviewer. You follow humans instructions strictly.
                 You optimize, fix and refactor provided answers with source code. Your code is modern and highly optimal.
                 You follow SOLID principles and good practices. You do not make comments or notes on the answer."""),
                ("human", "Please refactor all code blocks in the ANSWER below. Repeat the whole ANSWER as it is, but update code blocks. Start with 'ANSWER:'. \n\nANSWER:\n\n{code}\n")
            ]
        )

        parser = StrOutputParser()

        # Create LLM Chain
        self.intro_chain = prompt0 | llm0 | JsonOutputParser()
        self.input_chain = prompt1 | llm1 | parser
        self.review_chain = prompt2 | llm2 | parser

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
        self.responses = []

        intro = self._get_intro_text(input)
        yield from self._yield_text(intro['intro'])
        yield "\n\n"

        response = self._get_response_text(input)

        self.responses.append(response)
        yield from self._yield_text(intro['progress_answer'])

        for i in range(self.number_of_reviews):
            if i == self.number_of_reviews - 1:
                yield "\n\n---\n\n"
                stream = self.review_chain.stream({"code": response})
                final_response = ""
                for chunk in stream:
                    yield chunk
                    final_response += chunk
                self.responses.append(final_response)
            else:
                yield "\n\n"
                j = i % len(intro['wait_messages'])
                yield from self._yield_text(intro['wait_messages'][j])
                response= self._get_review_text(response)
                self.responses.append(response)

        yield "\n\n"

    def _get_intro_text(self, input):
        return self._get_default_intro()
        try:
            return self.intro_chain.invoke({"input": input})
        except Exception as e:
            return self._get_default_intro()

    def _get_response_text(self, input):
        response = self.input_chain.invoke({"input": input, "chat_history": self.chat_history})
        response = response.replace("ANSWER:", "")
        return response

    def _get_review_text(self, input):
        response = self.review_chain.invoke({"code": input})
        response = response.replace("ANSWER:", "")
        return response

    def _get_default_intro(self):
        return {
            "intro": "Hello! Your question is now being answered by multiple AI models. Please wait for a while.",
            "progress_answer": "Your answer is ready and it is being reviewed.",
            "wait_messages": ["Please wait for a while. I am reviewing your answer.", "Just a sec.", "Almost ready."]
        }

if __name__ == '__main__':

    chat = MultiChatChain()
    user_input = "Write a function that split string into a vector in C++17."
    stream = chat.stream(user_input)
    for chunk in stream:
        print(chunk, end="", flush=True)

    for response in chat.responses:
        print("\n\n---\n\n")
        print(response)

    # while True:
    #     user_input = input("\n\nYou: ")
    #     if user_input.lower() == 'exit':
    #         break

    #     stream = chat.stream(user_input)
    #     for chunk in stream:
    #         print(chunk, end="")