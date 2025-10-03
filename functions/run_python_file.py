def run_python_file(working_directory, file_path, args=[]):
    import os
    import subprocess
    rel_path = os.path.join(working_directory, file_path)
    abs_path = os.path.abspath(rel_path)
    try:
        if not abs_path.startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.exists(abs_path):
            return f'Error: File "{file_path}" not found.'
        
        if ".py" not in abs_path:
            return f'Error: "{file_path}" is not a Python file.'
        
        result = subprocess.run(["python3", abs_path] + args, capture_output=True, timeout=30)

        outcome = "Process exited with code " + str(result.returncode) if result.returncode != 0 else ""
        output = "No output produced." if not result.stdout else ""

        return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}\n{outcome}\n{output}"
    except Exception as e:
        return f"Error: executing Python file: {e}"