"""
這是一個用於比較兩個目錄中檔案差異的模組。
"""

import os
import time
import global_variable as gv

def move_file(file_name, source_directory, target_directory):
    """
    移動檔案從來源目錄到目標目錄。
    """
    source_file = os.path.join(source_directory, file_name)
    target_file = os.path.join(target_directory, file_name)
    os.rename(source_file, target_file)

# 開始計時
TIME_START = time.time()
print("開始執行")

MOVE_FILE_BOOLEAN = False

# 判斷 after directory 有，before directory 沒有的檔案
before_file_names = os.listdir(gv.before_file_directory)
after_file_names = os.listdir(gv.after_file_directory)

for file in before_file_names:
    if file in after_file_names:
        after_file_names.remove(file)

# 判斷 before directory 有，after directory 沒有的檔案
before_file_names_2 = os.listdir(gv.before_file_directory)
after_file_names_2 = os.listdir(gv.after_file_directory)

for file in after_file_names_2:
    if file in before_file_names_2:
        before_file_names_2.remove(file)

# 把結果寫入 txt 檔案
with open(os.path.join(gv.result_directory, "result.txt"), "w", encoding="utf-8") as f:
    f.write("before directory len: " + str(len(before_file_names)) + "\n")
    f.write("after directory len: " + str(len(after_file_names_2)) + "\n")
    f.write("----------------------------------------------")
    if before_file_names_2:
        f.write("before directory 有, after directory 沒有的檔案: "+ str(len(before_file_names_2)) + "\n")
        for file in before_file_names_2:
            f.write(file + "\n")

    f.write("\n")

    if after_file_names:
        f.write("after directory 有, before directory 沒有的檔案: "+ str(len(after_file_names)) + "\n")
        for file in after_file_names:
            f.write(file + "\n")

if MOVE_FILE_BOOLEAN:
    for file in before_file_names_2:
        move_file(file, gv.before_file_directory, gv.result_directory)

    for file in after_file_names:
        move_file(file, gv.after_file_directory, gv.result_directory)

# 結束計時
TIME_END = time.time()
print("花費時間: ", TIME_END - TIME_START, "秒")
