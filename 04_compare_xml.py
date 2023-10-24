'''
    對比xml, 並顯示不同之處
'''
import cProfile
import pstats
import csv
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor # io
# from concurrent.futures import ProcessPoolExecutor # cpu 操作
from lxml import etree as ET
import pandas as pd
import global_variable as gv

# 預先編譯正則表達式
patterns = [re.compile(p) for p in [
    '<TDSUFFIX2>.*</TDSUFFIX2>',
    '<TDCOVTITLE>.*</TDCOVTITLE>',
    '<TDDEST>.*</TDDEST>',
    '<TIMESTAMP>.*</TIMESTAMP>',
    '<CORR_KEY>.*?</CORR_KEY>',
    '<CORR_REQ_CREATION_DATE>.*</CORR_REQ_CREATION_DATE>',
    '<DELIVERYTIME>.*</DELIVERYTIME>',
    '<ACTIONTIME>.*</ACTIONTIME>',
    '<TERMINATION_REASON>.*</TERMINATION_REASON>', 
    '<TERMINATION_REASON />',
    '<CONTENT>.*</CONTENT>',
    '<ADDITIONAL_INFO_1>.*</ADDITIONAL_INFO_1>',
    '<ADDITIONAL_INFO_1 />'
]]


def reprocess_string(input_string):
    '''
    去除無需比對內容
    '''
    for pattern in patterns:
        input_string = pattern.sub('', input_string)
    return input_string


def find_first_n_text(element, find_numbers: int):
    '''
    獲取第n個出現的 text
    '''
    found_texts = []

    def helper(ele):
        nonlocal found_texts
        if len(found_texts) >= find_numbers:
            return

        if ele.text and ele.text.strip():
            found_texts.append(ele.text.strip())
            if len(found_texts) >= find_numbers:
                return

        for child in ele:
            helper(child)

    helper(element)

    if len(found_texts) >= find_numbers:
        return "_".join(found_texts[:find_numbers])
    if len(found_texts) > 0:
        return "_".join(found_texts)
    return None


def find_cd_post_doc_text(element):
    '''
    尋找是否有 <CD_POST_DOC> 的 text
    '''
    if element.tag == 'CD_POST_DOC' and element.text and element.text.strip():
        return element.text.strip()
    for child in element:
        result = find_cd_post_doc_text(child)
        if result:
            return result
    return None


def extract_blocks(tree):
    '''
    迭代第一層子節點，並將每個子節點的 key 與 index[] 存入 blocks
    blocks = {0: ["cd_post_doc", "first 5 text"], ....}
    
    針對每一個 blocks , 需要提供 key 來進行比對
    第一次比對用 cd_post_doc 或  first 3 text, 第二次比對用 first 5 text
    '''
    blocks = {}
    for index, child in enumerate(tree):
        cd_post_doc_key = find_cd_post_doc_text(child)
        if cd_post_doc_key:
            key = cd_post_doc_key
        else:
            key = find_first_n_text(child, 3)

        second_key = find_first_n_text(child, 5)
        blocks[index] = [key, second_key]
    return blocks

def is_valid_number(input_string):
    '''
    判斷是否為數字, 正確 '-1,234' or '1,234,567' or '123'
    '''
    # 匹配只有數字（不包含逗號）的情況
    if re.match(r'^-?\d{1,3}$', input_string):
        return True
    # 匹配包含逗號的數字格式
    return re.match(r'^-?\d{1,3}(,\d{3})+$', input_string) is not None

def remove_commas_and_convert(input_string):
    '''
    去除逗號, 變成 int
    '''
    return int(input_string.replace(',',''))

def find_differences(elem1, elem2, key, path='.'):
    '''
    find_differences 函數迭代形式
    '''
    stack = [(elem1, elem2, key, path)]
    differences = []

    while stack:
        cur_elem1, cur_elem2, cur_key, cur_path = stack.pop()

        if cur_elem1.tag != cur_elem2.tag:
            differences.append({"Key": cur_key,
                                "Path": cur_path,
                                "Type": "Tag Mismatch",
                                "Description": None ,
                                "Value": f"{cur_elem1.tag} != {cur_elem2.tag}"})
            continue

        if cur_elem1.attrib != cur_elem2.attrib:
            differences.append({"Key": cur_key,
                                "Path": cur_path,
                                "Type": "Attribute Mismatch",
                                "Description": None,
                                "Value": f"{cur_elem1.attrib} != {cur_elem2.attrib}"})
            continue

        text1 = cur_elem1.text.strip() if cur_elem1.text is not None else ""
        text2 = cur_elem2.text.strip() if cur_elem2.text is not None else ""

        if text1 != text2:

            differences_num = 0
            if is_valid_number(text1) and is_valid_number(text2):
                # 去掉逗號並轉為整數
                format_text1 = remove_commas_and_convert(text1)
                format_text2 = remove_commas_and_convert(text2)

                differences_num = format_text1 - format_text2

            differences.append({"Key": cur_key,
                                "Path": cur_path,
                                "Type": "Text Mismatch",
                                "Description": differences_num,
                                "Value": f"{text1} != {text2}"})

        # 將子節點添加到堆疊中
        children1 = list(cur_elem1)
        children2 = list(cur_elem2)

        for idx, (child1, child2) in enumerate(zip(children1, children2)):
            if len(child1) != len(child2):

                before_blocks = extract_blocks(child1)
                after_blocks = extract_blocks(child2)

                tag_name = child1[0].tag

                if len(before_blocks) > len(after_blocks):
                    success_matched_after_indices = []# 存儲成功對比的after索引
                    for before_index, before_key in before_blocks.items():
                        success_compare = False
                        before_first_key = before_key[0]
                        before_second_key = before_key[1]
                        before_child_path = f"{cur_path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]"

                        # 第一次: 使用 first key 比較
                        for after_index, after_key in after_blocks.items():
                            after_first_key = after_key[0]

                            if before_first_key == after_first_key:
                                stack.append((
                                    child1[before_index],
                                    child2[after_index],
                                    cur_key,
                                    before_child_path
                                            ))
                                success_matched_after_indices.append(after_index)
                                success_compare = True
                                del after_blocks[after_index]
                                break
                        # 第二次: 使用 second key 比較
                        if success_compare is False :
                            for after_index, after_key in after_blocks.items():
                                after_second_key = after_key[1]

                                if before_second_key == after_second_key:
                                    stack.append((
                                        child1[before_index],
                                        child2[after_index],
                                        cur_key,
                                        before_child_path
                                        ))
                                    success_matched_after_indices.append(after_index) #成功匹配的after索引
                                    success_compare = True
                                    del after_blocks[after_index]
                                    break

                        # 都比對不了，append before 內容
                        if success_compare is False:
                            differences.append({
                                "Key": cur_key,
                                "Path": before_child_path,
                                "Type": "Missing in after",
                                "Description": "Element is missing",
                                "Value": None
                                })
                            for elem in child1[before_index].iter():
                                differences.append({
                                    "Key": cur_key,
                                    "Path": before_child_path,
                                    "Type": "Show Missing",
                                    "Description": f"{elem.tag}",
                                    "Value": f"{elem.text}"
                                    })

                    # 沒有比對成功 after
                    success_after_set = set(success_matched_after_indices)
                    after_set = set(range(len(after_blocks)))
                    missing_after_set = after_set - success_after_set

                    for after_index in missing_after_set:
                        after_child_path = f"{cur_path}/{child1.tag}[{idx}]/{tag_name}[{after_index}]"
                        differences.append({
                            "Key": cur_key,
                            "Path": after_child_path,
                            "Type": "Miss match in after",
                            "Description": "Element is missing",
                            "Value": None
                            })
                        for elem in child2[after_index].iter():
                            differences.append({
                                "Key": cur_key,
                                "Path": after_child_path,
                                "Type": "Show Missing",
                                "Description": f"{elem.tag}",
                                "Value": f"{elem.text}"
                                })
                else: # len(after_blocks) > len(before_blocks):
                    success_matched_before_indices = []  # 存儲成功對比的before索引

                    for after_index, after_key in after_blocks.items():
                        success_compare = False
                        after_first_key = after_key[0]
                        after_second_key = after_key[1]
                        after_child_path = f"{cur_path}/{child2.tag}[{idx}]/{tag_name}[{after_index}]"

                        # 第一次: 使用 first key 比較
                        for before_index, before_key in before_blocks.items():
                            before_first_key = before_key[0]
                            if after_first_key == before_first_key:
                                stack.append((
                                    child1[before_index],
                                    child2[after_index],
                                    cur_key,
                                    after_child_path
                                ))
                                success_matched_before_indices.append(before_index) #成功匹配的before索引
                                success_compare = True
                                del before_blocks[before_index]
                                break

                        # 第二次: 使用 second key 比較
                        if success_compare is False:
                            for before_index, before_key in before_blocks.items():
                                before_second_key = before_key[1]

                                if after_second_key == before_second_key:
                                    stack.append((
                                        child1[before_index],
                                        child2[after_index],
                                        cur_key,
                                        after_child_path
                                        ))
                                    success_matched_before_indices.append(before_index) #成功匹配的before索引
                                    success_compare = True
                                    del before_blocks[before_index]
                                    break

                        # 都比對不了，append after 內容
                        if success_compare is False:
                            differences.append({
                                "Key": cur_key,
                                "Path": after_child_path,
                                "Type": "Missing in before",
                                "Description": "Element is missing",
                                "Value": None
                                })
                            for elem in child2[after_index].iter():
                                differences.append({
                                    "Key": cur_key,
                                    "Path": after_child_path,
                                    "Type": "Show Missing",
                                    "Description": f"{elem.tag}",
                                    "Value": f"{elem.text}"
                                    })

                    # 沒有比對成功 before
                    success_before_set = set(success_matched_before_indices)
                    before_set = set(range(len(before_blocks)))
                    missing_before_set = before_set - success_before_set

                    for before_index in missing_before_set:
                        before_child_path = f"{cur_path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]"
                        differences.append({
                            "Key": cur_key,
                            "Path": before_child_path,
                            "Type": "Miss match in before",
                            "Description": "Element is missing",
                            "Value": None
                            })
                        for elem in child1[before_index].iter():
                            differences.append({
                                "Key": cur_key,
                                "Path": before_child_path,
                                "Type": "Show Missing",
                                "Description": f"{elem.tag}",
                                "Value": f"{elem.text}"
                                })

            else:  # len(child1) == len(child2):
                child_path = f"{cur_path}/{child1.tag}[{idx}]"
                stack.append((child1, child2, cur_key, child_path))

        if len(children1) > len(children2):
            for idx, child in enumerate(children1[len(children2):]):
                differences.append({
                    "Key": cur_key,
                    "Path": f"{cur_path}/{child.tag}[{len(children2)+idx}]",
                    "Type": "Missing in after",
                    "Description": "Element is missing",
                    "Value": None
                    })
        elif len(children1) < len(children2):
            for idx, child in enumerate(children2[len(children1):]):
                differences.append({
                    "Key": cur_key,
                    "Path": f"{cur_path}/{child.tag}[{len(children1)+idx}]",
                    "Type": "Missing in before",
                    "Description": "Element is missing",
                    "Value": None
                    })

    return differences



def read_and_reprocess_file(file_path):
    '''
    開啟檔案，轉換成 string
    '''
    with open(file_path, "r", encoding="utf-8") as file:
        file_string = file.read()
    return reprocess_string(file_string)

# pylint: disable=c-extension-no-member
def process_file(file):
    '''
    處理檔案
    '''
    before_file_path = os.path.join(gv.before_file_directory, file)
    after_file_path = os.path.join(gv.after_file_directory, file)

    before_file_string = read_and_reprocess_file(before_file_path)
    after_file_string = read_and_reprocess_file(after_file_path)

    if before_file_string != after_file_string:
        before_root = ET.fromstring(before_file_string.encode('utf-8'))
        after_root = ET.fromstring(after_file_string.encode('utf-8'))

        differences = find_differences(before_root, after_root, key=file)
        return differences
    return []

def main():
    '''
    主程式  
    '''
    start_time = time.time()
    print("Start time: " + str(start_time))

    all_differences = []
    index = 0

    ## '''CPU操作'''
    # with ProcessPoolExecutor() as executor:
    #     for index, file in enumerate(os.listdir(gv.before_file_directory)):
    #         future = executor.submit(process_file, file)
    #         result = future.result()
    #         if result:
    #             all_differences.extend(result)

    #         if index % 1000 == 0:
    #             print(f"Processing {index + 1} files")
    ## ----------------------------------------------------------------------'''

    ## '''IO操作'''
    with ThreadPoolExecutor() as executor:
        for index, file in enumerate(os.listdir(gv.before_file_directory)):
            future = executor.submit(process_file, file)
            result = future.result()
            if result:
                all_differences.extend(result)

            if index % 1000 == 0:
                print(f"Processing {index + 1} files")
    ## '''----------------------------------------------------------------------'''

    ## '''正常執行'''
    # for index, file in enumerate(os.listdir(gv.before_file_directory)):
    #     before_file_path = os.path.join(gv.before_file_directory, file)
    #     after_file_path = os.path.join(gv.after_file_directory, file)

    #     before_file_string = read_and_reprocess_file(before_file_path)
    #     after_file_string = read_and_reprocess_file(after_file_path)

    #     if before_file_string != after_file_string:
    #         before_root = ET.fromstring(before_file_string.encode('utf-8'))
    #         after_root = ET.fromstring(after_file_string.encode('utf-8'))

    #         differences = find_differences(before_root, after_root, key = file)
    #         for d in differences:
    #             all_differences.append(d)

    #     if index % 1000 == 0:
    #         print(f"Processing {index + 1} files")
    ## ----------------------------------------------------------------------


    print(f"Total Processing {index + 1} files")

    output_df = pd.DataFrame(all_differences)
    output_file_path = os.path.join(gv.result_directory, "output.xlsx")
    output_df.to_excel(output_file_path, index=True)

    end_time = time.time()
    print("End time: " + str(end_time))
    print("Total time: " + str(end_time - start_time))


def convert_profile_to_csv(pstats_file, csv_file):
    '''
    把 pstats 轉成 csv
    '''
    stats = pstats.Stats(pstats_file)
    stats.sort_stats('cumulative')
    fieldnames = ['filename', 'line', 'func_name', 'ccalls', 'ncalls', 'ttot', 'cum_calls']
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for func, stat in stats.stats.items():
            filename, line, func_name = func
            # 使用 _ 來忽略未使用的變量
            ccalls, ncalls, ttot, cum_calls, _ = stat
            row_data = {
                'filename': filename,
                'line': line,
                'func_name': func_name,
                'ccalls': ccalls,
                'ncalls': ncalls,
                'ttot': ttot,
                'cum_calls': cum_calls
            }
            writer.writerow(row_data)


if __name__ == "__main__":
    # 是否產出報告
    OUTPUT_CPROFILE_FLAG = False

    if OUTPUT_CPROFILE_FLAG:
        PROFILE_FILE = 'profile_result.pstats'
        CSV_FILE = 'profile_result.csv'
        # 生成profile結果
        cProfile.run('main()', filename=PROFILE_FILE)
        convert_profile_to_csv(PROFILE_FILE, CSV_FILE)
    else:
        main()
