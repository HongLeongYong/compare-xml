# 從 txt 讀取檔案名稱，並複製到另一個資料夾
import os
import shutil
import global_variable as gv

# read file name from txt
file_list = []
with open(os.path.join(gv.result_directory,'need.txt'), "r", encoding="utf-8") as f:
    for line in f:
        file_list.append(line.replace('\n', ''))
    
# copy file to target directory
for file in file_list:
    # copy before file to target directory
    shutil.copy(os.path.join(gv.before_file_directory, file), gv.result_directory)
    # rename file
    os.rename(os.path.join(gv.result_directory, file), os.path.join(gv.result_directory, file.replace('.xml', '_before.xml')))

    # copy after file to target directory
    shutil.copy(os.path.join(gv.after_file_directory, file), gv.result_directory)
    # rename file
    os.rename(os.path.join(gv.result_directory, file), os.path.join(gv.result_directory, file.replace('.xml', '_after.xml')))
