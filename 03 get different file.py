import os
import time
import global_variable as gv

time_start = time.time()
print("開始執行 03 get different file.py")

before_has_after_not = []
after_has_before_not = []
# 判斷 before directory 有，after directory 沒有的檔案
for file in os.listdir(gv.before_file_directory):
    if file not in os.listdir(gv.after_file_directory):
        before_has_after_not.append(file)

for file in os.listdir(gv.after_file_directory):
    if file not in os.listdir(gv.before_file_directory):
        after_has_before_not.append(file)

# 把結果寫入 txt 檔案
with open(os.path.join(gv.result_directory, "result.txt"), "w", encoding="utf-8") as f:
    f.write("before directory 有，after directory 沒有的檔案:\n")
    for file in before_has_after_not:
        f.write(file + "\n")
    f.write("\n")
    f.write("after directory 有，before directory 沒有的檔案:\n")
    for file in after_has_before_not:
        f.write(file + "\n")
    f.write("\n")

time_end = time.time()
print("執行 03 get different file.py 花費時間: ", time_end - time_start, "秒")