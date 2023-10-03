'''
複製檔案到目標資料夾並重新命名
'''
import os
import shutil
import global_variable as gv

def copy_and_rename_files(file_list):
    '''
    loop through file_list
    '''
    for file_name in file_list:
        # Copy 'before' file to target directory and rename it
        copy_and_rename(file_name, gv.before_file_directory, '_before.xml')

        # Copy 'after' file to target directory and rename it
        copy_and_rename(file_name, gv.after_file_directory, '_after.xml')

def copy_and_rename(file_name, source_directory, suffix):
    '''
    Copy file from source directory to target directory and rename it
    '''
    shutil.copy(os.path.join(source_directory, file_name), gv.result_directory)
    os.rename(
        os.path.join(gv.result_directory, file_name),
        os.path.join(gv.result_directory, file_name.replace('.xml', suffix))
    )

if __name__ == "__main__":
    input_file_list = ['abc.xml', 'def.xml', 'ghi.xml']
    copy_and_rename_files(input_file_list)
