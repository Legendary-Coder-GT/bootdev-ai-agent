def write_file(working_directory, file_path, content):
    import os
    rel_path = os.path.join(working_directory, file_path)
    try:
        if not rel_path.startswith(working_directory):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
        with open(rel_path, 'w') as file:
            file.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error writing file "{file_path}": {str(e)}'