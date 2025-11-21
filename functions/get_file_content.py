import os
from pathlib import Path
from config import MAX_CHARS
from google.genai import types

schema_get_files_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Get a file's content in the specified path, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file_path to get content from, relative to the working directory. If not provided, returns Error string.",
            ),
        },
    ),
)


def get_file_content(working_directory, file_path):
    try:
        w_dir = Path(working_directory).resolve()
        t_file = (w_dir / file_path).resolve()
        if not t_file.is_relative_to(w_dir):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(t_file.__str__()):
            return f'Error: File not found or is not a regular file: "{file_path}"'

    except Exception as exc:
        return f"Error: {exc}"

    try:
        with open(t_file.__str__(), "r") as f:
            file_content_string = f.read(MAX_CHARS + 1)
            if len(file_content_string) == MAX_CHARS + 1:
                file_content_string = (
                    file_content_string[:MAX_CHARS]
                    + f'[...File "{file_path}" truncated at 10000 characters]'
                )
            return file_content_string
    except Exception:
        return f"Error: couldn't open {file_path}"
