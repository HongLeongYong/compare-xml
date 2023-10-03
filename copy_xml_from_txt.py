'''
從 txt 讀取檔案名稱，並複製到另一個資料夾
'''
import os
import shutil
import global_variable as gv

# read file name from txt
file_list = []
with open(os.path.join(gv.result_directory, 'need.txt'), "r", encoding="utf-8") as f:
    for line in f:
        file_list.append(line.replace('\n', ''))

# copy file to target directory
for file in file_list:
    # copy before file to target directory
    before_ori_filepath = os.path.join(gv.before_file_directory, file)
    shutil.copy(before_ori_filepath, gv.result_directory)
    # rename file
    renamed_before_file = file.replace('.xml', '_before.xml')
    before_unrename_filepath = os.path.join(gv.result_directory, file)
    before_renamed_filepath = os.path.join(gv.result_directory, renamed_before_file)
    os.rename(before_unrename_filepath, before_renamed_filepath)
    
    # copy after file to target directory
    after_ori_filepath = os.path.join(gv.after_file_directory, file)
    shutil.copy(after_ori_filepath, gv.result_directory)
    # rename file
    renamed_after_file = file.replace('.xml', '_after.xml')
    after_unrename_filepath = os.path.join(gv.result_directory, file)
    after_renamed_filepath = os.path.join(gv.result_directory, renamed_after_file)
    os.rename(after_unrename_filepath, after_renamed_filepath)
