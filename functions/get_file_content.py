import os
from google.genai import types
from functions.config import MAX_CHARS

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read file contents, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read contents from, relative to the working directory. If not provided, read file contents in the working directory itself.",
            ),
        },
    ),
)

def get_file_content(working_directory, file_path):
    try:
        full_path = os.path.join(working_directory, file_path)
        fp_abs = os.path.abspath(full_path)
        wd_abs = os.path.abspath(working_directory)
        if not (fp_abs == wd_abs or fp_abs.startswith(wd_abs + os.sep)):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        elif not os.path.isfile(fp_abs):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        else:
            with open(fp_abs, "r") as f:
                file_content_string = f.read()
            if len(file_content_string) > MAX_CHARS:
                new_string = file_content_string[:MAX_CHARS] + f' [...File "{file_path}" truncated at {MAX_CHARS} characters]'
                return new_string
            else:
                return file_content_string
    except Exception as e:
        return f'Error: {e}'
