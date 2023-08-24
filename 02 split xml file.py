import os
import time
import global_variable as gv
import xml.etree.ElementTree as ET

# method： 分割 xml 檔案
def split_xml_file(filename, destination_directory):
    xml_file = open(filename, "r", encoding="utf-8")
    xml_string = xml_file.read()
    xml_file.close()

    # 取代掉不需要的標籤
    xml_string = xml_string.replace("<sf>", "")
    xml_string = xml_string.replace("</sf>", "")

    # 加入特殊標籤做分割
    xml_string = xml_string.replace("</asx:abap>", "</asx:abap>@@@qq###")
    xml_obj_array = xml_string.split("@@@qq###")
    xml_obj_array.pop(len(xml_obj_array) - 1)

    for xml_obj in xml_obj_array:
        tree = ET.ElementTree(ET.fromstring(xml_obj))
        root = tree.getroot()

        # file name
        cc_num = root.find('.//CC_NUM').text
        template_id = root.find('.//TEMPLATE_ID').text

        # xml_declaration 表示是否要加入 xml 宣告
        tree.write(os.path.join(destination_directory, cc_num + "_" + template_id + ".xml"),
                    encoding="utf-8", xml_declaration=True)



# 設定目標🎯檔案路徑
destination = gv.before_file_directory
if not os.path.exists(destination):
    os.makedirs(destination)

# loop 需要處理的資料夾
for file in os.listdir(gv.before_big_file_directory):
    split_xml_file(filename = os.path.join(gv.before_big_file_directory, file), 
                   destination_directory = gv.before_file_directory)

