#  loop 資料夾底下的檔案，並且更改檔案名稱
import os
import global_variable as gv

def run(directory):
    # 設定副檔名
    file_type = ".xml"

    for file in os.listdir(directory):
        os.rename(os.path.join(directory, file), os.path.join(directory, file + file_type))
        
    # 顯示 for 的總數量
    print("Total: " + str(len(os.listdir(directory))))

# -------------------------------------------------------------------------------
run(gv.before_big_file_directory)
run(gv.after_big_file_directory)


