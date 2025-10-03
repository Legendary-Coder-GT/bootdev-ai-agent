import os
import sys
from dotenv import load_dotenv
from call_function import call_function

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, default to application name",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads a text file (up to an internal character limit) if and only if it resides inside the permitted working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, default to application name"
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file, joined to the working_directory (e.g., 'today.txt')."
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes the provided text content to a file joined under the working directory, enforcing the directory boundary.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="Absolute or normalized base directory within which all file access must occur."
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Destination path joined to the working_directory (e.g., 'output/report.txt')."
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Raw text content to write to the file."
            ),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file located under the working directory with optional CLI-style arguments and returns stdout/stderr.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="Absolute or normalized base directory within which all execution must occur."
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Python script path joined to the working_directory (e.g., 'scripts/main.py'). Must include '.py'."
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional list of string arguments passed to the script (default: [])."
            ),
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file
    ]
)

client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.

# Examples
## Ex. 1
Q: Give me information on XYZ application in the repo and how it works.
A: Calling tool get_files_info({working_directory: "XYZ"})
Calling tool get_file_content({working_directory: "XYZ", file_path: "main.py"})

Based on the code, it seems the XYZ application scrapes data from websites.
Would you like me to run the application?

## Ex. 2
Q: Fix the bug in the XYZ application that is causing it to crash.
A: Calling tool get_files_info({working_directory: "XYZ"})
Calling tool get_file_content({working_directory: "XYZ", file_path: "main.py"})
Calling tool run_python_file({working_directory: "XYZ", file_path: "main.py", args: [...]})
Calling tool get_files_info({working_directory: "XYZ/pkg"})
Calling tool get_file_content({working_directory: "XYZ", file_path: "pkg/utils.py"})
Calling tool get_file_content({working_directory: "XYZ", file_path: "pkg/scraper.py"})
Calling tool write_file({working_directory: "XYZ", file_path: "pkg/scraper.py", content: "..."})

I found the issue in pkg/scraper.py and fixed it (missing import statement).
The application should no longer crash.

# Notes
- All applications are folder names under the working directory.
- Use get_files_info first ALWAYS to confirm the folder has main.py in it.
- Always use the available functions to interact with the filesystem or run code.
- The code for the application will always be stored in "main.py"
"""

def main():
    if len(sys.argv) == 1:
        print("Please provide a prompt as a command-line argument.")
        sys.exit(1)
    messages = [
        types.Content(role="user", parts=[types.Part(text=sys.argv[1])]),
    ]
    exit_flag = False
    counter = 1
    while not exit_flag and counter <= 20:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt
                    )
            )
            for candidate in response.candidates:
                messages.append(candidate.content)

            if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
                verbosity = True
            else:
                verbosity = False

            if response.text is not None:
                if verbosity:
                    print(f"User prompt: {sys.argv[1]}")
                    usage_data = response.usage_metadata
                    print(f"Prompt tokens: {usage_data.prompt_token_count}")
                    print(f"Response tokens: {usage_data.candidates_token_count}")
                exit_flag = True
                print(response.text)
                

            if response.function_calls is not None:
                content = call_function(response.function_calls[0], verbose=verbosity)
                if len(content.parts[0].function_response.response) > 0:
                    material = content.parts[0].function_response.response
                    print(f"-> {material}") 
                    messages.append(types.Content(role="user", parts=[types.Part(text=str(material))]))
                else:
                    raise Exception("Content not returned from function call")
            
            counter += 1
        except Exception as e:
            print(f"Error: {e}")
            exit_flag = True
    

if __name__ == "__main__":
    main()
