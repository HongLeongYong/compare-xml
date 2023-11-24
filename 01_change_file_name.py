"""此模組用於在目錄中重新命名檔案並附加檔案副檔名。"""
import os
import global_variable as gv  # 引入全局變量模組

def run(directory):
    """在指定的目錄中重新命名檔案並附加檔案副檔名。
    
    參數:
        directory (str): 包含需要重新命名的檔案的目錄。
    """
    file_type = ".xml"  # 要附加的檔案副檔名
    for file in os.listdir(directory):
        os.rename(os.path.join(directory, file), os.path.join(directory, file + file_type))
    print("總數: " + str(len(os.listdir(directory))))

# 執行函數
run(gv.before_big_file_directory)
run(gv.after_big_file_directory)

# 輸出結果