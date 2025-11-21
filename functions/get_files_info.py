import os
from pathlib import Path
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)


def get_files_info(working_directory, directory="."):
    try:
        w_dir = Path(working_directory).resolve()
        t_dir = (w_dir / directory).resolve()
        if not t_dir.is_relative_to(w_dir):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(t_dir.__str__()):
            return f'Error: "{directory}" is not a directory'
    except Exception as exc:
        return f"Error: {exc}"

    files = os.listdir(t_dir)
    filesinfo = list(
        map(
            lambda x: f"- {x}: file_size={os.path.getsize((t_dir / x).__str__())} bytes, is_dir={os.path.isdir((t_dir / x).__str__())}",
            files,
        )
    )
    return "\n".join(filesinfo)
