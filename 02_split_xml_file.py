"""
此模組用於讀取 XML 檔案，將其分割成多個段落，並儲存為新的 XML 檔案。
"""

import os
import time
import xml.etree.ElementTree as ET
from collections import Counter
import matplotlib.pyplot as plt
import global_variable as gv

def split_and_save_xml_segments(filename, destination_directory, frequency_dict):
    """
    讀取 XML 檔案，將其分割成多個段落，並儲存為新的 XML 檔案。
    """

    with open(filename, "r", encoding="utf-8") as xml_file:
        xml_string = xml_file.read()

    xml_string = xml_string.replace("<sf>", "").replace("</sf>", "")
    xml_string = xml_string.replace("</asx:abap>", "</asx:abap>@@@qq###")
    xml_segments = xml_string.split("@@@qq###")
    xml_segments.pop()

    for xml_segment in xml_segments:
        tree = ET.ElementTree(ET.fromstring(xml_segment))
        root = tree.getroot()

        try:
            doc_temp_id = root.find('.//DOC_TEMP_ID').text
            # if doc_temp_id in gv.z005_list: print(f'z005: {doc_temp_id}')
            # if doc_temp_id in gv.z006_list: print(f'z006: {doc_temp_id}')
            bp_id = root.find('.//BUSINESS_PARTNER_ID').text
            commission_contract = root.find('.//COMMISSION_CONTRACT').text
            policy_id = root.find('.//POLICY_ID').text
            if policy_id is None:
                policy_id = root.find('.//POLICY1').text
        except AttributeError:
            if policy_id is None:
                policy_id = "None"

        # 計算出現次數
        composite_key = f"{doc_temp_id}_{bp_id}_{commission_contract}_{policy_id}"
        if composite_key in frequency_dict:
            frequency_dict[composite_key] += 1
        else:
            frequency_dict[composite_key] = 1

        output_name = f"{doc_temp_id}_{bp_id}_{commission_contract}_{policy_id}_{frequency_dict[composite_key]}.xml"
        output_name = output_name.replace('/', '_')

        tree.write(os.path.join(destination_directory, output_name),
                   encoding="utf-8", xml_declaration=True)


def process_files_in_directory(from_path, destination_path, frequency_dict):
    '''
    遍歷指定目錄下的所有 XML 檔案，將其分割並儲存到目標目錄。
    '''
    time_start = time.time()
    print(f"Start time: {time_start}")

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    sorted_file_list = sorted(os.listdir(from_path))

    for index, file in enumerate(sorted_file_list):
        split_and_save_xml_segments(filename = os.path.join(from_path, file),
                                    destination_directory = destination_path,
                                    frequency_dict = frequency_dict)
        if index % 100 == 0:
            print(f"Processing {index + 1} files")

    time_end = time.time()
    print(f"End time: {time_end}")
    print(f"Total time: {time_end - time_start}")

def format_pie_chart_labels(pct, allvals):
    """
    格式化餅圖的標籤。

    參數:
    pct (float): 當前區塊的百分比。
    allvals (list): 包含所有區塊值的列表。

    返回值:
    str: 顯示絕對頻率和百分比的格式化字串。
    """
    # 計算絕對頻率（經過四捨五入）
    absolute = int(round(pct / 100. * sum(allvals)))
    # 使用 f-string 返回格式化字串
    return f"{absolute} xml \n({pct:1.1f}%)"

def draw_pie_chart(*data_dicts):
    """
    繪製餅狀圖來表示 data_dicts 中各個值的出現頻率。
    """
    plt.figure(figsize=(20, 10))

    for index, data_dict in enumerate(data_dicts, start=1):
        plt.subplot(1, len(data_dicts), index)

        frequency_counter = Counter(data_dict.values())
        labels = [f"{k} times" for k in frequency_counter.keys()]
        sizes = list(frequency_counter.values())
        colors = ['#7B99FA', '#53CDD8', '#96EAB7', 'F1F3B8']
        explode = [0.1] * len(labels)

        # 使用 functools.partial 或額外的參數來傳遞 sizes
        autopct = lambda pct, sizes=sizes: format_pie_chart_labels(pct, sizes)

        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct=autopct, shadow=True, startangle=90)
        plt.axis('equal')
        plt.title(f'Distribution of Key Frequencies {index}')

    plt.show()

def main():
    """
    主函數，負責調用其他函數以完成 XML 檔案的分割和儲存, before 和 after 分別處理。
    """
    composite_key_frequency_dict_before = {}
    composite_key_frequency_dict_after = {}

    process_files_in_directory(gv.before_big_file_directory, gv.before_file_directory, composite_key_frequency_dict_before)
    process_files_in_directory(gv.after_big_file_directory, gv.after_file_directory, composite_key_frequency_dict_after)

    # before - 印出出現次數>= 2 的 key 值
    for key, value in composite_key_frequency_dict_before.items():
        if value >= 2:
            print(f"before key '{key}' appears {value} times.")
    print('-' * 50)
    # after - 印出出現次數>= 2 的 key 值
    for key, value in composite_key_frequency_dict_after.items():
        if value >= 2:
            print(f"after key '{key}' appears {value} times.")

    draw_pie_chart(composite_key_frequency_dict_before, composite_key_frequency_dict_after)

if __name__ == "__main__":
    main()
