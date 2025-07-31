import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to write a file to, relative to the working directory. If not provided, write file in the working directory itself.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file."
            )
        },
    ),
)

def write_file(working_directory, file_path, content):
    full_path = os.path.join(working_directory, file_path)
    fp_abs = os.path.abspath(full_path)
    wd_abs = os.path.abspath(working_directory)
    try:
        if not (fp_abs == wd_abs or fp_abs.startswith(wd_abs + os.sep)):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        elif not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path))
            with open(file_path, "w") as f:
                f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        else:
            with open(file_path, "w") as f:
                f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error: {e}'
