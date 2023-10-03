"""
此模組用於分割 XML 檔案。
"""

import os
import time
import xml.etree.ElementTree as ET
import global_variable as gv  # 自定義模組放在標準模組之後

# 常數名稱改為大寫
DESTINATION = gv.before_file_directory

def split_xml_file(filename, destination_directory):
    """
    此函數用於分割 XML 檔案。
    """
    # 使用 'with' 語句來自動關閉檔案
    with open(filename, "r", encoding="utf-8") as xml_file:
        xml_string = xml_file.read()

    # 取代掉不需要的標籤
    xml_string = xml_string.replace("<sf>", "").replace("</sf>", "")

    # 加入特殊標籤做分割
    xml_string = xml_string.replace("</asx:abap>", "</asx:abap>@@@qq###")
    xml_obj_array = xml_string.split("@@@qq###")
    xml_obj_array.pop()

    for xml_obj in xml_obj_array:
        tree = ET.ElementTree(ET.fromstring(xml_obj))
        root = tree.getroot()

        # 檔案名稱
        cc_num = root.find('.//CC_NUM').text
        template_id = root.find('.//TEMPLATE_ID').text

        # xml_declaration 表示是否要加入 xml 宣告
        tree.write(os.path.join(destination_directory, f"{cc_num}_{template_id}.xml"),
                   encoding="utf-8", xml_declaration=True)

def main():
    """
    主函數。
    """
    time_start = time.time()
    print(f"Start time: {time_start}")

    if not os.path.exists(DESTINATION):
        os.makedirs(DESTINATION)

    for index, file in enumerate(os.listdir(gv.before_big_file_directory)):
        split_xml_file(filename=os.path.join(gv.before_big_file_directory, file),
                       destination_directory=DESTINATION)
        if index % 100 == 0:
            print(f"Processing {index + 1} files")

    time_end = time.time()
    print(f"End time: {time_end}")
    print(f"Total time: {time_end - time_start}")

if __name__ == "__main__":
    main()
