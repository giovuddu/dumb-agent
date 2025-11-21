import os
from pathlib import Path
import subprocess
from google.genai import types


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes the python file in the specified file file_path, constrained to the working directory. Only files with .py extensions are enabled",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file_path to execute, relative to the working directory. If not provided, returns Error string.",
            ),
            "args": types.Schema(
                type=types.Type.STRING,
                description="The array to pass as arguments to the executable python file.",
            ),
        },
    ),
)


def run_python_file(working_directory, file_path, args=[]):
    try:
        w_dir = Path(working_directory).resolve()
        t_file = (w_dir / file_path).resolve()
        if not t_file.is_relative_to(w_dir):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(t_file.__str__()):
            return f'Error: File "{file_path}" not found.'
        if not t_file.__str__().endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

    except Exception as exc:
        return f"error: {exc}"

    try:
        completed_process = subprocess.run(
            ["python3", t_file.__str__(), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
        res = ""
        if completed_process.returncode != 0:
            res += "Process exited with code {completed_process.returncode}"
        if (
            completed_process.stdout is not None
            and completed_process.stderr is not None
        ):
            res += f"""
STDOUT: {completed_process.stdout}
STDERR: {completed_process.stderr}
            """
        if res == "":
            return "No output produced"
        return res

    except Exception as exc:
        return f"Error: executing Python file: {exc}"
