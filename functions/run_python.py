import subprocess
import os
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file in the working directory. Can be called with just a filename - arguments are optional.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path to run python files from, relative to the working directory. If not provided, run python files in the working directory itself.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional command-line arguments for the python file. Leave empty if no arguments are needed.",
            ),
        },
        required=["file_path"],
    ),
)

def run_python_file(working_directory, file_path, args=None):
    if args is None:
        args = []
    full_path = os.path.join(working_directory, file_path)
    fp_abs = os.path.abspath(full_path)
    wd_abs = os.path.abspath(working_directory)
    try:
        if not (fp_abs == wd_abs or fp_abs.startswith(wd_abs + os.sep)):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        elif not os.path.exists(fp_abs):
            return f'Error: File "{file_path}" not found.'
        elif not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file.'
        else:
            result = subprocess.run(["python", fp_abs, *args], capture_output=True, cwd=working_directory, timeout=30)
            if result.stdout and result.stderr:
                if result.returncode != 0:
                    return f"STDOUT: {result.stdout.decode()}\nSTDERR: {result.stderr.decode()}\nProcess exited with code {result.returncode}"
                else:
                    return f"STDOUT: {result.stdout.decode()}\nSTDERR: {result.stderr.decode()}"
            elif result.stdout:
                return f"STDOUT: {result.stdout.decode()}"
            elif result.stderr:
                if result.returncode != 0:
                    return f"STDERR: {result.stderr.decode()}\nProcess exited with code {result.returncode}"
                else:
                    return f"STDERR: {result.stderr.decode()}"
            else:
                return "No output produced."
    except Exception as e:
        return f"Error: executing Python file: {e}"
            
