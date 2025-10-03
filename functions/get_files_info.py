def get_files_info(working_directory, directory="."):
    import os

    try:
        rel_path = os.path.join(working_directory, directory)
        full_path = os.path.abspath(rel_path)
        abs_working_directory = os.path.abspath(working_directory)
        if not full_path.startswith(abs_working_directory + os.sep) and full_path != abs_working_directory:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(full_path):
            return f'Error: "{directory}" is not a directory'
        file_list = []
        for file in os.listdir(full_path):
            string = ""
            string += "- " + file + ": file_size=" + str(os.path.getsize(full_path + os.sep + file)) + " bytes, is_dir=" + str(os.path.isdir(full_path + os.sep + file))
            file_list.append(string)
        return "\n".join(file_list)
    except Exception as e:
        return f"Error: {str(e)}"
