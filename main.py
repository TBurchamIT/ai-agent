import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.run_python import run_python_file, schema_run_python_file
from functions.write_file import write_file, schema_write_file

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]
)
user_prompt = sys.argv[1]
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

if len(sys.argv) < 2:
    print("Error: No Prompt Provided")
    sys.exit(1)
else:
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
    )

MAX_ITERATIONS = 20
VERBOSE = "--verbose" in sys.argv

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_map = {
        'get_files_info': get_files_info,
        'get_file_content': get_file_content,
        'run_python_file': run_python_file,
        'write_file': write_file
    }
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    args = function_call_part.args or {}
    args["working_directory"] = "./calculator"
    try:
        function_result = function_map[function_name](**args)
    except Exception as e:
        function_result = {"error": str(e)}

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


# def main():
#     if response.function_calls:
#         for function_call in response.function_calls:
#             function_call_result = call_function(function_call, verbose=VERBOSE)
#             if function_call_result.parts[0].function_response.response:
#                 if VERBOSE:
#                     print(f"-> {function_call_result.parts[0].function_response.response}")
#             else:
#                 raise Exception("No response returned from function call.")
#     else:
#         print(response.text)
#         if "--verbose" in sys.argv:
#             print(f"User prompt: {user_prompt}")
#             print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
#             print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

def main():
    try:
        for i in range(MAX_ITERATIONS):
            if VERBOSE:
                print(f"\n--- Iteration {i + 1} ---")

            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_prompt,
                ),
            )

            for candidate in response.candidates:
                if candidate.content:
                    messages.append(candidate.content)

            # If any candidate returned a text response, we're done
            if response.text:
                print(f"\n✅ Final response:\n{response.text}")
                break

            # Handle function calls
            if response.function_calls:
                for function_call in response.function_calls:
                    # Call the function and get the result message
                    tool_response = call_function(function_call, verbose=VERBOSE)

                    # Append the tool response to messages
                    messages.append(tool_response)
            else:
                # No function calls and no text? Fail-safe exit.
                print("⚠️ No function calls or final text response found.")
                break

        else:
            print("⚠️ Reached maximum iterations without final response.")

    except Exception as e:
        print(f"❌ Agent failed: {e}")



if __name__ == "__main__":
    main()
