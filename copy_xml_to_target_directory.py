# copy xml file to target directory
import os
import global_variable as gv
import shutil

file_list = ['abc.xml', 'def.xml', 'ghi.xml']


for file in file_list:
    # copy before file to target directory
    shutil.copy(os.path.join(gv.before_file_directory, file), gv.result_directory)
    # rename file
    os.rename(os.path.join(gv.result_directory, file), os.path.join(gv.result_directory, file.replace('.xml', '_before.xml')))

    # copy after file to target directory
    shutil.copy(os.path.join(gv.after_file_directory, file), gv.result_directory)
    # rename file
    os.rename(os.path.join(gv.result_directory, file), os.path.join(gv.result_directory, file.replace('.xml', '_after.xml')))
