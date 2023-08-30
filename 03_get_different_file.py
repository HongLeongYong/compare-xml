import os
import time
import global_variable as gv


def move_file(file_name, source_directory, target_directory):
    source_file = os.path.join(source_directory, file_name)
    target_file = os.path.join(target_directory, file_name)
    os.rename(source_file, target_file)


time_start = time.time()
print("開始執行")

move_file_boolean = False

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

if move_file_boolean:
    for file in before_file_names_2:
        move_file(file, gv.before_file_directory, gv.result_directory)

    for file in after_file_names:
        move_file(file, gv.after_file_directory, gv.result_directory)


time_end = time.time()
print("花費時間: ", time_end - time_start, "秒")