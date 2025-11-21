import os
from pathlib import Path
from google.genai import types


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write content to the specified file path, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file_path to write content to, relative to the working directory. If not provided, returns Error string.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write in the specified file_path. Write mode is replace_all. NOT APPEND.",
            ),
        },
    ),
)


def write_file(working_directory, file_path, content):
    try:
        w_dir = Path(working_directory).resolve()
        t_file = (w_dir / file_path).resolve()
        if not t_file.is_relative_to(w_dir):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        if not os.path.isdir(t_file.parents[0].__str__()):
            os.makedirs(t_file.parents[0].__str__())

    except Exception as exc:
        return f"Error: {exc}"

    try:
        with open(t_file.__str__(), "w") as f:
            f.write(content)
    except Exception:
        return f'Error: File could not be written: "{file_path}"'
    else:
        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )
