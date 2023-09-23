# 對比xml，並顯示不同之處
import os
import re
import time
import pandas as pd 
import xml.etree.ElementTree as ET
import global_variable as gv

# 獲取第一個、第二個和第三個出現的 text 並指定為 key
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

# 迭代第一層子節點，並將每個子節點的 key 與 index 存入 blocks
def extract_blocks(tree):
    blocks = []
    for index, child in enumerate(tree):
        cd_post_doc_key = find_cd_post_doc_text(child)
        if cd_post_doc_key:
            key = cd_post_doc_key
        else:
            key = find_first_n_text(child, 3)
        blocks.append((index, key))
    return blocks

# 迭代第一層子節點，並將每個子節點的 key 與 index 存入 blocks
def extract_blocks_second_compare(tree):
    blocks = []
    for index, child in enumerate(tree):
        key = find_first_n_text(child, 5)
        blocks.append((index, key))
    return blocks

# 處理 string， 需要去除一些重複的字串
def reprocess_string(input_string):
    input_string = re.sub('<TDSUFFIX2>.*</TDSUFFIX2>', '', input_string)
    input_string = re.sub('<TDCOVTITLE>.*</TDCOVTITLE>', '', input_string)
    input_string = re.sub('<TDDEST>.*</TDDEST>', '', input_string)
    input_string = re.sub('<TIMESTAMP>.*</TIMESTAMP>', '', input_string)
    input_string = re.sub('<CORR_KEY>.*?</CORR_KEY>', '', input_string)
    input_string = re.sub('<CORR_REQ_CREATION_DATE>.*</CORR_REQ_CREATION_DATE>', '', input_string)
    return input_string


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
"""
def is_valid_number(s):
    return re.match(r'-?\d+(,\d{3})*$', s) is not None


def remove_commas_and_convert(s):
    # Replace all commas
    s = re.sub(r'[,]', '', s)
    # Convert into integer
    return int(s)

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

            before_blocks_second_compare = extract_blocks_second_compare(child1)
            after_blocks_second_compare = extract_blocks_second_compare(child2)

            tag_name = child1[0].tag

            if len(before_blocks) > len(after_blocks):
                after_dict = {key: index for index, key in after_blocks}
                after_dict_second_compare = {key: index for index, key in after_blocks_second_compare}
                success_matched_after_indices = []  # 存儲成功對比的after索引

                for before_index, before_key in before_blocks:
                    after_index = after_dict.get(before_key)
                    if after_index is not None:
                        child_path = f"{path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]"
                        differences.extend(find_differences(child1[before_index], child2[after_index], key=key, path=child_path))
                        success_matched_after_indices.append(after_index) #成功匹配的after索引
                    else:
                        # 如果抓取不了，就要使用前4個 text 當成 key, 然後再次進行比對
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
         
                    
            else:
                before_dict = {key: index for index, key in before_blocks}
                success_matched_before_indices = []  # 存儲成功對比的before索引

                for after_index, after_key in after_blocks:
                    before_index = before_dict.get(after_key)
                    if before_index is not None:
                        child_path = f"{path}/{child2.tag}[{idx}]/{tag_name}[{before_index}]"
                        differences.extend(find_differences(child1[before_index], child2[after_index], key=key, path=child_path))
                        success_matched_before_indices.append(before_index) #成功匹配的before索引
                    else:
                        # 如果抓取不了，就要使用前4個 text 當成 key, 然後再次進行比對
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
        else:
            child_path = f"{path}/{child1.tag}[{idx}]"
            differences.extend(find_differences(child1, child2, key= key, path=child_path))

    if len(children1) > len(children2):
        for idx, child in enumerate(children1[len(children2):]):
            differences.append({"Key": key, "Path": f"{path}/{child.tag}[{len(children2)+idx}]", "Type": "Missing in after", "Description": "Element is missing", "Value": None})
    elif len(children1) < len(children2):
        for idx, child in enumerate(children2[len(children1):]):
            differences.append({"Key": key, "Path": f"{path}/{child.tag}[{len(children1)+idx}]", "Type": "Missing in before", "Description": "Element is missing", "Value": None})

    return differences

# ---------------------------------------------------------------------
# 主程式
# ---------------------------------------------------------------------

start_time = time.time()
print("Start time: " + str(start_time))

output_df = pd.DataFrame()

for index, file in enumerate(os.listdir(gv.before_file_directory)):
    before_file = open(os.path.join(gv.before_file_directory, file), "r", encoding="utf-8")
    before_file_string = before_file.read()
    before_file.close()
    before_file_string = reprocess_string(before_file_string)

    after_file = open(os.path.join(gv.after_file_directory, file), "r", encoding="utf-8")
    after_file_string = after_file.read()
    after_file.close()
    after_file_string = reprocess_string(after_file_string)

    if before_file_string != after_file_string:
        before_tree = ET.ElementTree(ET.fromstring(before_file_string))
        before_root = before_tree.getroot()

        after_tree = ET.ElementTree(ET.fromstring(after_file_string))
        after_root = after_tree.getroot()

        differences = find_differences(before_root, after_root, key = file)
        output_df = pd.concat([output_df, pd.DataFrame(differences)], axis=0).reset_index(drop=True)

    if index % 500 == 0:
        print(f"Processing {index + 1} files")

    ## break point
    # if index == 1000:
    #     break
print(f"Processing {index + 1} files")

output_df.to_excel(os.path.join(gv.result_directory, "output.xlsx"), index=True)

end_time = time.time()
print("End time: " + str(end_time))
print("Total time: " + str(end_time - start_time))