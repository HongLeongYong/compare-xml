# 對比xml，並顯示不同之處
import os
import re
import time
import pandas as pd 
# import xml.etree.ElementTree as ET
from lxml import etree as ET
import global_variable as gv
from concurrent.futures import ThreadPoolExecutor

# 預先編譯正則表達式
patterns = [re.compile(p) for p in [
    '<TDSUFFIX2>.*</TDSUFFIX2>',
    '<TDCOVTITLE>.*</TDCOVTITLE>',
    '<TDDEST>.*</TDDEST>',
    '<TIMESTAMP>.*</TIMESTAMP>',
    '<CORR_KEY>.*?</CORR_KEY>',
    '<CORR_REQ_CREATION_DATE>.*</CORR_REQ_CREATION_DATE>'
]]

# 去除無需比對內容
def reprocess_string(input_string):
    for pattern in patterns:
        input_string = pattern.sub('', input_string)
    return input_string

# 獲取第n個出現的 text
def find_first_n_text(element, n: int):
    found_texts = []

    def helper(ele):
        nonlocal found_texts
        if len(found_texts) >= n:
            return

        if ele.text and ele.text.strip():
            found_texts.append(ele.text.strip())
            if len(found_texts) >= n:
                return

        for child in ele:
            helper(child)

    helper(element)

    if len(found_texts) >= n:
        return "_".join(found_texts[:n])
    elif len(found_texts) > 0:
        return "_".join(found_texts)
    else:
        return None
    
# 尋找是否有 <CD_POST_DOC> 的 text
def find_cd_post_doc_text(element):
    if element.tag == 'CD_POST_DOC' and element.text and element.text.strip():
        return element.text.strip()
    for child in element:
        result = find_cd_post_doc_text(child)
        if result:
            return result
    return None

# 迭代第一層子節點，並將每個子節點的 key 與 index[] 存入 blocks
# blocks = {0: ["cd_post_doc", "first 5 text"], ....}
def extract_blocks(tree):
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


"""
    Return whether the string s is a valid number.
    A valid number is an optional negative sign followed by
    one or more digits followed by any number of comma-separated
    groups of three digits.

    >>> is_valid_number('123')
    True
    >>> is_valid_number('-1,234')
    True
    >>> is_valid_number('1,234,567')
    True
    >>> is_valid_number('12,34,567')
    False
    >>> is_valid_number('1234567')
    False
"""
# 判斷是否為數字
def is_valid_number(s):
    # 匹配只有數字（不包含逗號）的情況
    if re.match(r'^-?\d{1,3}$', s):
        return True
    # 匹配包含逗號的數字格式
    return re.match(r'^-?\d{1,3}(,\d{3})+$', s) is not None

# 去除逗號, 變成 int
def remove_commas_and_convert(s):
    return int(s.replace(',',''))

# 對比兩個 element，並將不同之處存入 differences
def find_differences(elem1, elem2, key, path='.'):
    differences = []

    if elem1.tag != elem2.tag:
        differences.append({"Key": key, "Path": path, "Type": "Tag Mismatch","Description": None , "Value": f"{elem1.tag} != {elem2.tag}"})
        
    if elem1.attrib != elem2.attrib:
        differences.append({"Key": key, "Path": path, "Type": "Attribute Mismatch","Description": None,  "Value": f"{elem1.attrib} != {elem2.attrib}"})

    text1 = elem1.text.strip() if elem1.text is not None else ""
    text2 = elem2.text.strip() if elem2.text is not None else ""

    differences_num = 0
    if is_valid_number(text1) and is_valid_number(text2):
        # 去掉逗號並轉為整數
        format_text1 = remove_commas_and_convert(text1)
        format_text2 = remove_commas_and_convert(text2)

        # 相減
        differences_num = format_text1 - format_text2

    if text1 != text2:
        differences.append({"Key": key, "Path": path, "Type": "Text Mismatch","Description": differences_num , "Value": f"{text1} != {text2}"})

    children1 = list(elem1)
    children2 = list(elem2)
    
    for idx, (child1, child2) in enumerate(zip(children1, children2)):
        #如果 child 數量不相等
        if len(child1) != len(child2):

            before_blocks = extract_blocks(child1)
            after_blocks = extract_blocks(child2)

            tag_name = child1[0].tag

            if len(before_blocks) > len(after_blocks):
                success_matched_after_indices = []  # 存儲成功對比的after索引                

                for before_index, before_key in before_blocks.items():
                    success_compare = False
                    before_first_key = before_key[0]
                    before_second_key = before_key[1]
                    
                    # 第一次: 使用 first key 比較
                    for after_index, after_key in after_blocks.items():
                        after_first_key = after_key[0]

                        if before_first_key == after_first_key:
                            child_path = f"{path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]"
                            differences.extend(find_differences(child1[before_index], child2[after_index], key=key, path=child_path))
                            success_matched_after_indices.append(after_index) 
                            success_compare = True
                            del after_blocks[after_index]
                            break
                    
                    # 第二次: 使用 second key 比較
                    if success_compare == False :
                        for after_index, after_key in after_blocks.items():
                            after_second_key = after_key[1]

                            if before_second_key == after_second_key:
                                child_path = f"{path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]"
                                differences.extend(find_differences(child1[before_index], child2[after_index], key=key, path=child_path))
                                success_matched_after_indices.append(after_index) #成功匹配的after索引
                                success_compare = True
                                del after_blocks[after_index]
                                break

                    # 都比對不了，append before 內容
                    if success_compare == False:
                        differences.append({"Key": key, "Path": f"{path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]", "Type": "Missing in after", "Description": "Element is missing", "Value": None})
                        for elem in child1[before_index].iter():
                            differences.append({"Key": key, "Path": f"{path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]", "Type": "Show Missing", "Description": f"{elem.tag}" , "Value": f"{elem.text}"})

                # 沒有比對成功 after
                success_after_set = set(success_matched_after_indices)
                after_set = set(range(len(after_blocks)))
                missing_after_set = after_set - success_after_set

                for after_index in missing_after_set:
                    differences.append({"Key": key, "Path": f"{path}/{child1.tag}[{idx}]/{tag_name}[{after_index}]", "Type": "Miss match in after", "Description": "Element is missing", "Value": None})
                    for elem in child2[after_index].iter():
                        differences.append({"Key": key, "Path": f"{path}/{child2.tag}[{idx}]/{tag_name}[{after_index}]", "Type": "Show Missing", "Description": f"{elem.tag}" , "Value": f"{elem.text}"})
         
                    
            else: # len(after_blocks) > len(before_blocks):
                success_matched_before_indices = []  # 存儲成功對比的before索引

                for after_index, after_key in after_blocks.items():
                    success_compare = False
                    after_first_key = after_key[0]
                    after_second_key = after_key[1]

                    # 第一次: 使用 first key 比較
                    for before_index, before_key in before_blocks.items():
                        before_first_key = before_key[0]                        
                        
                        if after_first_key == before_first_key:
                            child_path = f"{path}/{child2.tag}[{idx}]/{tag_name}[{before_index}]"
                            differences.extend(find_differences(child1[before_index], child2[after_index], key=key, path=child_path))
                            success_matched_before_indices.append(before_index) #成功匹配的before索引
                            success_compare = True
                            del before_blocks[before_index]
                            break

                    # 第二次: 使用 second key 比較
                    if success_compare == False:
                        for before_index, before_key in before_blocks.items():
                            before_second_key = before_key[1]

                            if after_second_key == before_second_key:
                                child_path = f"{path}/{child2.tag}[{idx}]/{tag_name}[{before_index}]"
                                differences.extend(find_differences(child1[before_index], child2[after_index], key=key, path=child_path))
                                success_matched_before_indices.append(before_index) #成功匹配的before索引
                                success_compare = True
                                del before_blocks[before_index]
                                break

                    # 都比對不了，append after 內容
                    if success_compare == False:
                        differences.append({"Key": key, "Path": f"{path}/{child2.tag}[{idx}]/{tag_name}[{after_index}]", "Type": "Missing in before", "Description": "Element is missing", "Value": None})
                        for elem in child2[after_index].iter():
                            differences.append({"Key": key, "Path": f"{path}/{child2.tag}[{idx}]/{tag_name}[{after_index}]", "Type": "Show Missing", "Description": f"{elem.tag}" , "Value": f"{elem.text}"})

                # 沒有比對成功 before
                success_before_set = set(success_matched_before_indices)
                before_set = set(range(len(before_blocks)))
                missing_before_set = before_set - success_before_set

                for before_index in missing_before_set:
                    differences.append({"Key": key, "Path": f"{path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]", "Type": "Miss match in before", "Description": "Element is missing", "Value": None})
                    for elem in child1[before_index].iter():
                        differences.append({"Key": key, "Path": f"{path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]", "Type": "Show Missing", "Description": f"{elem.tag}" , "Value": f"{elem.text}"})

        else:  # len(child1) == len(child2):
            child_path = f"{path}/{child1.tag}[{idx}]"
            differences.extend(find_differences(child1, child2, key= key, path=child_path))

    if len(children1) > len(children2):
        for idx, child in enumerate(children1[len(children2):]):
            differences.append({"Key": key, "Path": f"{path}/{child.tag}[{len(children2)+idx}]", "Type": "Missing in after", "Description": "Element is missing", "Value": None})
    elif len(children1) < len(children2):
        for idx, child in enumerate(children2[len(children1):]):
            differences.append({"Key": key, "Path": f"{path}/{child.tag}[{len(children1)+idx}]", "Type": "Missing in before", "Description": "Element is missing", "Value": None})

    return differences


def read_and_reprocess_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        file_string = f.read()
    return reprocess_string(file_string)

def process_file(file):
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
    start_time = time.time()
    print("Start time: " + str(start_time))

    all_differences = []

    with ThreadPoolExecutor() as executor:
        for index, file in enumerate(os.listdir(gv.before_file_directory)):
            future = executor.submit(process_file, file)
            result = future.result()
            if result:
                all_differences.extend(result)

            if index % 1000 == 0:
                print(f"Processing {index + 1} files")

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

    print(f"Total Processing {index + 1} files")

    output_df = pd.DataFrame(all_differences)
    output_file_path = os.path.join(gv.result_directory, "output.xlsx")
    output_df.to_excel(output_file_path, index=True)

    end_time = time.time()
    print("End time: " + str(end_time))
    print("Total time: " + str(end_time - start_time))

if __name__ == "__main__":
    main()