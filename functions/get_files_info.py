import os
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
    full_path = os.path.abspath(os.path.join(working_directory, directory))
    wd_abs = os.path.abspath(working_directory)
    try:
        if not (full_path == wd_abs or full_path.startswith(wd_abs + os.sep)):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        elif os.path.isdir(full_path) == False:
            return f'Error: "{directory}" is not a directory'
        else:
            dir_list = os.listdir(full_path)
            string_list = []
            for item in dir_list:
                size = os.path.getsize(os.path.join(full_path, item))
                is_dir = os.path.isdir(os.path.join(full_path, item))
                string_list.append(f'- {item}: file_size={size} bytes, is_dir={is_dir}')
            return '\n'.join(string_list)
    except Exception as e:
        return f'Error: {e}'
