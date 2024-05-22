import re
import os
import hashlib
from typing import List, Tuple
from subprocess import CalledProcessError, CompletedProcess

from workflows.lib.ActiveParserAction import ActiveParserAction

import subprocess
import threading

class CodeBlock:
    def __init__(self, file_path: str, language: str, code: str, executable: bool = False):
        self.file_path = file_path
        self.language = language
        self.code = code
        self.code_md5 = hashlib.md5(code.encode()).hexdigest()
        self.executable = executable

    def save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w') as file:
            file.write(self.code)

    def execute(self, timeout: int) -> CompletedProcess:
        return run_bash_script(self.file_path, timeout)

def run_bash_script(script_path: str, timeout: int) -> CompletedProcess:
    def target(process):
        process.communicate()

    script_dir = os.path.dirname(script_path)
    script_name = os.path.basename(script_path)
    command = ""
    if script_name.endswith(".py"):
        command = f"/bin/bash -c 'python3 ./{script_name}'"
    else:
        command = f"/bin/bash -e ./{script_name}"

    print("Command: " + command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=script_dir)
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


class CodeExecActiveParser:

    def __init__(self, output_dir: str, session_id: str, max_parser_feedbacks: int = 3):
        self.output_dir = output_dir
        self.session_id = session_id
        self.max_parser_feedbacks = max_parser_feedbacks
        self.code_blocks = []

    def parse(self, response, feedback_count):
        print("Parsing response...", flush=True)

        action = ActiveParserAction()
        action.feedback = None
        action.info = ""

        self.code_blocks += self.extract_code_blocks(response)
        count = len(self.code_blocks)
        print("Extracted " + str(count) + " code blocks", flush=True)

        for block in self.code_blocks:
            print("---- code block ----", flush=True)
            print("File path: " + block.file_path, flush=True)
            print("Language: " + block.language, flush=True)
            print("Code: " + block.code, flush=True)
            print("Code MD5: " + block.code_md5, flush=True)
            print("Executable: " + str(block.executable), flush=True)
            print("--------------------", flush=True)

        self.write_code_blocks(self.code_blocks)

        all_ok = True
        for block in self.code_blocks:
            if block.executable:
                print(f"Executing {block.file_path}")
                result = block.execute(timeout=60)
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
                action.info += os.getenv("TREE_CLONE_INFO_TEMPLATE", None).replace("[[session_id]]", self.session_id)
                action.feedback = None

        print("Done", flush=True)
        return action

    def extract_code_blocks(self, text: str) -> List[CodeBlock]:
        matched_blocks = self.match_code_blocks(text)

        file_path_pattern = re.compile(r'(.?[\w_/]+\.\w+).*\s+```\w*', re.MULTILINE)

        cleanText = self.cleanup_markdown(text)

        file_paths = list(file_path_pattern.finditer(cleanText))

        # print("Clean text:\n\n\n" + cleanText + "\n\n\n")

        print("File paths:")
        for path in file_paths:
            print(path.group(1))

        result = []
        unnamed_count = 1
        last_pos = 0

        for line, language, code in matched_blocks:
            print("Line: " + line)
            file_path = None

            # Find the last file path before this code block
            for path_match in file_path_pattern.finditer(cleanText, last_pos):
                if path_match.end() < text.find(code, last_pos):
                    file_path = path_match.group(1)
                    last_pos = path_match.end()
                else:
                    break

            executable = False
            if "execute" in line or "run" in line:
                executable = True

            if file_path is None:
                ext = "txt"
                if language:
                    if language == "python":
                        ext = "py"
                    elif language == "bash":
                        ext = "sh"
                    else:
                        ext = language
                    file_path = f"unnamed_{unnamed_count}.{ext}"
                else:
                    file_path = f"unnamed_{unnamed_count}.{ext}"
                unnamed_count += 1

            file_path = os.path.join(self.output_dir, file_path)
            result.append(CodeBlock(self.undecorate(file_path), language, code.strip(), executable))

        self.markExecutedIfMentioned(result, cleanText)

        # check if last item is bash/sh:
        # if len(result) > 0 and result[-1].language == "sh" or result[-1].language == "bash":
        #     result[-1].executable = True

        return result

    def match_code_blocks(self, text) -> List[Tuple[str, str, str]]:
        code_block_pattern = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)

        code_blocks = []
        for match in code_block_pattern.finditer(text):
            language = match.group(1)
            if language is None:
                language = 'sh'

            # print("Matched language: " + language)
            code = match.group(2)
            start_pos = match.start()

            # Find the preceding line by searching backwards from the start_pos
            preceding_line_end = text.rfind('\n', 0, start_pos)
            preceding_line_start = text.rfind('\n', 0, preceding_line_end) + 1
            preceding_line = text[preceding_line_start:preceding_line_end].strip()

            code_blocks.append((preceding_line, language, code))

        return code_blocks

    def markExecutedIfMentioned(self, blocks: List[CodeBlock], text: str) -> None:
        text = self.undecorate(text)
        for block in blocks:
            filename = os.path.basename(block.file_path)
            pattern = re.compile(r'\b(execute)[\s:./]*' + filename + r'\b', re.IGNORECASE)
            if pattern.search(text):
                block.executable = True

    def cleanup_markdown(self, file_name: str) -> str:
        return re.sub(r'[*"\']', '', file_name)

    def undecorate(self, file_name: str) -> str:
        return re.sub(r'[*`"\']', '', file_name)

    def write_code_blocks(self, blocks: List[CodeBlock]) -> None:
        dir = os.path.join(self.output_dir, self.session_id)
        if not os.path.exists(dir):
            os.makedirs(dir)
        for block in blocks:
            block.save()


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

