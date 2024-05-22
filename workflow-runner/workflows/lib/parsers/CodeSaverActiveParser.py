from workflows.lib.ActiveParserAction import ActiveParserAction

import re
import os
from typing import List, Tuple

class CodeSaverActiveParser:

  def __init__(self, output_dir: str, session_id: str):
    self.output_dir = output_dir
    self.session_id = session_id

  def parse(self, response, feedback_count):
    print("Parsing response...", flush=True)
    action = ActiveParserAction()
    action.feedback = None
    action.info = None

    extracted = self.extract_code_blocks(response)
    count = len(extracted)
    print("Extracted " + str(count) + " code blocks", flush=True)

    info = os.getenv("TREE_CLONE_INFO_TEMPLATE", None)
    if count > 0 and info is not None:
      # replace [[SESSION_ID]] with self.session_id
      info = info.replace("[[session_id]]", self.session_id)
      action.info = info

    for file_path, code in extracted:
      print(f"File Path: {file_path}")
      print(f"Code: {code}\n")

    self.write_code_blocks(extracted)

    print("Done", flush=True)
    return action

  def extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
    # Regular expressions to match file paths and code blocks
    file_path_pattern = re.compile(r'(?:^|\n)([^\s]+\.[^\s]+)(?=\n)')
    code_block_pattern = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)

    # Find all code blocks
    code_blocks = code_block_pattern.findall(text)

    # Find all file paths
    file_paths = file_path_pattern.findall(text)

    # Prepare the result list
    result = []
    last_pos = 0
    unnamed_count = 1

    for language, code in code_blocks:
        # Find the last file path before this code block
        file_path = None
        for path_match in file_path_pattern.finditer(text, last_pos):
            if path_match.end() < text.find(code, last_pos):
                file_path = path_match.group(1)
                last_pos = path_match.end()
            else:
                break

        if file_path:
            result.append((self.clean_file_name(file_path), code.strip()))
        else:
            # Generate a default file name
            print("No filepath before code block", flush=True)
            print("Language: " + language, flush=True)

            extension = language if language else "txt"
            name_base = "unnamed"

            # rename to run.sh or run_n.sh if no file path is given and it's shell script
            if language == "sh" or language == "bash":
                extension = "sh"
                name_base = "run"

            if unnamed_count == 1:
                result.append((f"{name_base}.{extension}", code.strip()))
            else:
                result.append((f"{name_base}_{unnamed_count}.{extension}", code.strip()))
            unnamed_count += 1

    return result

  def clean_file_name(self, file_name: str) -> str:
    """
    Remove markdown characters like asterisks and underscores from the file name.
    """
    return re.sub(r'[*`"\']', '', file_name)

  def write_code_blocks(self, file_contents: List[Tuple[str, str]]) -> None:
    """
    Write code blocks to files. If file paths contain subdirectories, create them if they do not exist.

    Args:
        file_contents (List[Tuple[str, str]]): List of tuples where each tuple contains a file path and the corresponding code content.
    """
    for file_path, content in file_contents:
        path = self.output_dir + "/" + file_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Write the content to the file
        with open(path, 'w') as file:
            file.write(content)
