import re
import os
import hashlib
from typing import List, Tuple
from subprocess import CalledProcessError, CompletedProcess

from workflows.lib.ActiveParserAction import ActiveParserAction

import subprocess
import threading


class CodeBlock:
    def __init__(self, file_path: str, code: str, execute: bool = False):
        self.file_path = file_path
        self.code = code
        self.execute = execute


    def save(self, prefix = "./"):
        path = os.path.join(prefix, self.file_path)
        dir = os.path.dirname(path)
        if dir != '' and not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        with open(path, 'w') as file:
            file.write(self.code)

    def execute_code(self, cwd, timeout: int) -> CompletedProcess:
        def target(process):
            process.communicate()

        script_name = os.path.basename(self.file_path)
        command = ""
        if script_name.endswith(".py"):
            command = f"/bin/bash -c 'python3 ./{script_name}'"
        else:
            command = f"/bin/bash -e ./{script_name}"

        print("Command: " + command)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
        thread = threading.Thread(target=target, args=(process,))
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            process.terminate()
            thread.join()

        output, error = process.communicate()
        exit_code = process.returncode
        print("Exit code: " + str(exit_code))
        print("Output: " + output)
        print("Error: " + error) if error else None
        return CompletedProcess(command, exit_code, output, error)

class LiveCodeActiveParser:
    """
    We expect this format:

[<response>]

[<file_path>]./file/path.extension[</file_path>]
[<code>]
source code
[</code>]
[<execute>]false[</execute>]
[<explanation>]
explanation
[</explanation>]

[<file_path>]./script_name.sh[</file_path>]
[<code>]
commands
[</code>]
[<execute>]true[</execute>]
[<explanation>]
explanation
[</explanation>]

[</response>]
    """
    def __init__(self, output_dir: str, session_id: str, enable_execution: bool = False, max_parser_feedbacks: int = 3):
        self.output_dir = output_dir
        self.session_id = session_id
        self.enable_execution = enable_execution
        self.max_parser_feedbacks = max_parser_feedbacks
        self.code_blocks = []

        self.buffer = ""
        self.current_block = None
        self.current_field = ""

    def parse_live(self, chunk: str) -> str:
        # print("Parsing chunk: " + chunk, flush=True)
        if chunk == "[<EOM>]":
            return self.parse_line(self.buffer, True)

        output = ""
        # buffer full line
        self.buffer += chunk

        if "\n" in self.buffer:
            # print("Buffer contains a line: " + self.buffer, flush=True)
            output = self.parse_line(self.buffer)
            self.buffer = ""

        return output

    def parse_line(self, line: str, eom = False) -> str:
        if eom and self.current_block is not None:
            self.code_blocks.append(self.current_block)

        value = self.parse_tag(line, "file_path")
        if value is not None:
            if self.current_block is not None:
                self.code_blocks.append(self.current_block)
            self.current_block = CodeBlock(file_path=value, code="", execute=False)
            return "**" + value + "**\n"

        value = self.parse_tag(line, "execute")
        if value is not None:
            if value.lower() == "true":
                self.current_block.execute = True
                return ""
            else:
                return ""

        if self.has_start_tag(line, "code"):
            self.current_field = "code"
            return "```\n"
        if self.has_end_tag(line, "code"):
            self.current_field = ""
            return "```\n"
        if self.has_start_tag(line, "explanation"):
            return "\n"
        if self.has_end_tag(line, "explanation"):
            return "\n"

        if self.has_start_tag(line, "response") or self.has_end_tag(line, "response"):
            return ""

        if self.current_field == "code":
            self.current_block.code += line

        return line


    def has_start_tag(self, line: str, tag: str) -> bool:
        return "[<" + tag + ">]" in line

    def has_end_tag(self, line: str, tag: str) -> bool:
        return "[</" + tag + ">]" in line

    def parse_tag(self, line: str, tag: str) -> str:
        if not self.has_start_tag(line, tag):
            return None
        if not self.has_end_tag(line, tag):
            return None
        return line[line.find("[<" + tag + ">]") + len("[<" + tag + ">]"):line.find("[</" + tag + ">]")]

    def parse(self, response, feedback_count):
        print("Parsing response...", flush=True)
        # print(response, flush=True)

        action = ActiveParserAction()
        action.feedback = None
        action.info = ""

        count = len(self.code_blocks)
        print("Extracted " + str(count) + " code blocks", flush=True)
        for block in self.code_blocks:
            print("---- code block ----", flush=True)
            print("File path: " + block.file_path, flush=True)
            print("Code: " + block.code, flush=True)
            print("Execute: " + str(block.execute), flush=True)
            print("--------------------", flush=True)

        self.write_code_blocks(self.code_blocks)

        tree_info = os.getenv("TREE_CLONE_INFO_TEMPLATE", None).replace("[[session_id]]", self.session_id)
        if not self.enable_execution:
            action.info = tree_info
            return action

        all_ok = True
        for block in self.code_blocks:
            if block.execute:
                print(f"Executing {block.file_path}")
                result = block.execute_code(self.output_dir, timeout=60)
                if result.returncode != 0:
                    print(f"Execution of {block.file_path} failed with exit code {result.returncode}")
                    all_ok = False
                    action.feedback = "Code execution failed with exit code " + str(result.returncode)
                    if result.stderr:
                        action.feedback += " and error:\n" + result.stderr
                        action.info += ("\n\nExecuting " + os.path.basename(block.file_path)
                            + " failed:\n\n```plain\n" + result.stderr + "```\n\n")
                    break
                else: # on success
                    action.info += ("\n\nExecution succeded:\n\n"
                        + "```plain\n" + result.stdout + "```\n\n")

        if all_ok or feedback_count > self.max_parser_feedbacks:
            if count > 0 and action.info is not None:
                action.info += tree_info
                action.feedback = None

        print("Done", flush=True)
        return action
    # def extract_code_blocks(self, text: str) -> List[CodeBlock]:
    #     yaml_block = self.extract_first_block(text)
    #     result = self.parse_yaml_block(yaml_block)
    #     return result


    def write_code_blocks(self, blocks: List[CodeBlock]) -> None:
        for block in blocks:
            block.save(self.output_dir)


if __name__ == '__main__':
    # Example usage 1
    parser = CodeExecActiveParser(output_dir='/tmp', session_id='example_session_id')
    response = """
    Intro text.
    app.py:
    ```python
    print("Hello from the app!")
    ```

    and you can execute python:
    ```python
    print("Hello from the python code to launch!")
    ```

    Then more text.
    ```sh
    echo "This should NOT be launched"
    ```

    and run some bad code:
    ```sh
    echo "Fix me and launch me!"
    exit 0
    ```

    and finally:
    ```sh
    echo "This should be launched"
    ```
    """

    # we expect: app.py unnamed_1.python run_2.sh run_3.sh run_4.sh
    feedback_count = 1
    action = parser.parse(response, feedback_count)

