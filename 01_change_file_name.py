"""Module for renaming files in a directory and appending a file extension."""
import os
import global_variable as gv

def run(directory):
    """Rename files in the given directory and append a file extension.
    
    Args:
        directory (str): The directory containing the files to be renamed.
    """
    file_type = ".xml"
    for file in os.listdir(directory):
        os.rename(os.path.join(directory, file), os.path.join(directory, file + file_type))
    print("Total: " + str(len(os.listdir(directory))))

run(gv.before_big_file_directory)
run(gv.after_big_file_directory)
