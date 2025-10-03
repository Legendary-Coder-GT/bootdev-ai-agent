def get_file_content(working_directory, file_path):
    import os
    from functions.config import MAX_CHARS
    file_path = os.path.join(working_directory, file_path)
    try:
        if not file_path.startswith(working_directory):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.isfile(file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        
        with open(file_path, 'r') as file:
            file_content_string = file.read(MAX_CHARS)
            if len(file_content_string) == MAX_CHARS:
                file_content_string += f'[...File "{file_path}" truncated at 10000 characters]'
            return file_content_string
    except Exception as e:
        return f'Error reading file "{file_path}": {str(e)}'    