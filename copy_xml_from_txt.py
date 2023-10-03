'''
從 need.txt 讀取檔案名稱，並從 before 和 after 資料夾複製檔案到 result 資料夾，並重新命名
'''
import os
import shutil
import global_variable as gv


def copy_and_rename_files(file_names_list, ori_directory, new_suffix):
    '''
    複製和重新命名 before 和 after 檔案
    '''
    for file_name in file_names_list:
        ori_filepath = os.path.join(ori_directory, file_name)
        shutil.copy(ori_filepath, gv.result_directory)

        renamed_file = file_name.replace('.xml', new_suffix)
        unrenamed_filepath = os.path.join(gv.result_directory, file_name)
        renamed_filepath = os.path.join(gv.result_directory, renamed_file)

        os.rename(unrenamed_filepath, renamed_filepath)


if __name__ == "__main__":
    # 讀取檔案名稱
    with open(os.path.join(gv.result_directory, 'need.txt'), "r", encoding="utf-8") as f:
        file_list = [line.strip() for line in f]

    # 複製和重新命名 before 和 after 檔案
    copy_and_rename_files(file_list, gv.before_file_directory, '_before.xml')
    copy_and_rename_files(file_list, gv.after_file_directory, '_after.xml')
