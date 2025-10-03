from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file

func_dict = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}

def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Function call: {function_call_part.name} with arguments {function_call_part.args}")
    else:
        print(f" - Calling function: {function_call_part.name}")
    
    working_directory = "./calculator"
    if function_call_part.name not in func_dict.keys():
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )
    else:
        func = func_dict[function_call_part.name]
        kwargs = dict(function_call_part.args)
        kwargs["working_directory"] = working_directory
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": func(**kwargs)},
                )
            ],
        )
