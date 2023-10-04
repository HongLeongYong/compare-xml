"""
此模組用於讀取 XML 檔案，將其分割成多個段落，並儲存為新的 XML 檔案。
"""

import os
import time
import xml.etree.ElementTree as ET
from collections import Counter
import matplotlib.pyplot as plt
import global_variable as gv

# 初始化一個空字典來存儲合成鍵和其出現次數
composite_key_frequency_dict = {}

def split_and_save_xml_segments(filename, destination_directory):
    """
    讀取 XML 檔案，將其分割成多個段落，並儲存為新的 XML 檔案。
    """
    global composite_key_frequency_dict # pylint: disable=global-variable-not-assigned

    with open(filename, "r", encoding="utf-8") as xml_file:
        xml_string = xml_file.read()

    xml_string = xml_string.replace("<sf>", "").replace("</sf>", "")
    xml_string = xml_string.replace("</asx:abap>", "</asx:abap>@@@qq###")
    xml_segments = xml_string.split("@@@qq###")
    xml_segments.pop()

    for segment_index, xml_segment in enumerate(xml_segments):
        tree = ET.ElementTree(ET.fromstring(xml_segment))
        root = tree.getroot()

        doc_temp_id = root.find('.//DOC_TEMP_ID').text
        bp_id = root.find('.//BUSINESS_PARTNER_ID').text
        commission_contract = root.find('.//COMMISSION_CONTRACT').text
        policy_id = root.find('.//POLICY_ID').text

        output_name = f"{doc_temp_id}_{bp_id}_{commission_contract}_{policy_id}_{segment_index}.xml"
        output_name = output_name.replace('/', '_')

        tree.write(os.path.join(destination_directory, output_name),
                   encoding="utf-8", xml_declaration=True)

        # 計算出現次數
        composite_key = f"{doc_temp_id}_{bp_id}_{commission_contract}_{policy_id}"
        if composite_key in composite_key_frequency_dict:
            composite_key_frequency_dict[composite_key] += 1
        else:
            composite_key_frequency_dict[composite_key] = 1

def process_files_in_directory(from_path, destination_path):
    '''
    遍歷指定目錄下的所有 XML 檔案，將其分割並儲存到目標目錄。
    '''
    time_start = time.time()
    print(f"Start time: {time_start}")

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    sorted_file_list = sorted(os.listdir(from_path))

    for index, file in enumerate(sorted_file_list):
        split_and_save_xml_segments(filename=os.path.join(from_path, file),
                                    destination_directory=destination_path)
        if index % 100 == 0:
            print(f"Processing {index + 1} files")

    time_end = time.time()
    print(f"End time: {time_end}")
    print(f"Total time: {time_end - time_start}")

def draw_pie_chart(data_dict):
    """
    繪製餅狀圖來表示 data_dict 中各個值的出現頻率。
    """
    frequency_counter = Counter(data_dict.values())

    labels = [f"{k} times" for k in frequency_counter.keys()]
    sizes = list(frequency_counter.values())
    colors = ['blue', 'red', 'green', 'yellow']  # 添加更多顏色，如果有更多種出現次數
    explode = [0.1] * len(labels)  # 將所有部分都突出顯示

    plt.figure(figsize=(10, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')  # 確保餅狀圖是個圓形
    plt.title('Distribution of Key Frequencies')
    plt.show()

def main():
    """
    主函數，負責調用其他函數以完成 XML 檔案的分割和儲存。
    """
    process_files_in_directory(gv.before_big_file_directory, gv.before_file_directory)
    process_files_in_directory(gv.after_big_file_directory, gv.after_file_directory)

    # 調用繪製餅狀圖的方法
    draw_pie_chart(composite_key_frequency_dict)

if __name__ == "__main__":
    main()
