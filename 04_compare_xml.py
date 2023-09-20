# 對比xml，並顯示不同之處
import os
import global_variable as gv
import re
import xml.etree.ElementTree as ET
import pandas as pd 
import time

# 獲取第一個出現的 text 並指定為 key
def find_first_text(element):
    if element.text and element.text.strip():
        return element.text.strip()
    
    for child in element:
        text = find_first_text(child)
        if text:
            return text
    return None

# 迭代第一層子節點，並將每個子節點的 key 與 index 存入 blocks
def extract_blocks(tree):
    blocks = []
    for i, child in enumerate(tree):
        key = find_first_text(child)
        blocks.append((index,key))
    return blocks

def reprocess_string(input_string):
    input_string = re.sub('<TDSUFFIX2>.*</TDSUFFIX2>', '', input_string)
    input_string = re.sub('<TDCOVTITLE>.*</TDCOVTITLE>', '', input_string)
    input_string = re.sub('<TDDEST>.*</TDDEST>', '', input_string)
    input_string = re.sub('<TIMESTAMP>.*</TIMESTAMP>', '', input_string)
    input_string = re.sub('<CORR_KEY>.*?</CORR_KEY>', '', input_string)
    input_string = re.sub('<CORR_REQ_CREATION_DATE>.*</CORR_REQ_CREATION_DATE>', '', input_string)
    return input_string

def find_differences(elem1, elem2, key, path='.'):
    differences = []

    if elem1.tag != elem2.tag:
        differences.append({"Key": key, "Path": path, "Type": "Tag Mismatch", "Description": f"{elem1.tag} != {elem2.tag}"})
        
    if elem1.attrib != elem2.attrib:
        differences.append({"Key": key, "Path": path, "Type": "Attribute Mismatch", "Description": f"{elem1.attrib} != {elem2.attrib}"})

    text1 = elem1.text.strip() if elem1.text is not None else ""
    text2 = elem2.text.strip() if elem2.text is not None else ""

    if text1 != text2:
        differences.append({"Key": key, "Path": path, "Type": "Text Mismatch", "Description": f"{text1} != {text2}"})

    children1 = list(elem1)
    children2 = list(elem2)
    
    for idx, (child1, child2) in enumerate(zip(children1, children2)):
        #如果 child 數量不相等
        if len(child1) != len(child2):

            before_blocks = extract_blocks(child1)
            after_blocks = extract_blocks(child2)

            tag_name = child1[0].tag

            if len(before_blocks) > len(after_blocks):
                after_dict = {key: index for index, key in after_blocks}

                for before_index, before_key in before_blocks:
                    after_index = after_dict.get(before_key)
                    if after_index is not None:
                        child_path = f"{path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]"
                        differences.extend(find_differences(child1[before_index], child2[after_index], key=key, path=child_path))
                    else:
                        differences.append({"Key": key, "Path": f"{path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]", "Type": "Missing in after", "Description": "Element is missing"})
                        for elem in child1[before_index].iter():
                            differences.append({"Key": key, "Path": f"{path}/{child1.tag}[{idx}]/{tag_name}[{before_index}]", "Type": "Show Missing", "Description": f"{elem.tag} : {elem.text}"})

            else:
                before_dict = {key: index for index, key in before_blocks}

                for after_index, after_key in after_blocks:
                    before_index = before_dict.get(after_key)
                    if before_index is not None:
                        child_path = f"{path}/{child2.tag}[{idx}]/{tag_name}[{before_index}]"
                        differences.extend(find_differences(child1[before_index], child2[after_index], key=key, path=child_path))
                    else:
                        differences.append({"Key": key, "Path": f"{path}/{child2.tag}[{idx}]/{tag_name}[{after_index}]", "Type": "Missing in before", "Description": "Element is missing"})
                        for elem in child2[after_index].iter():
                            differences.append({"Key": key, "Path": f"{path}/{child2.tag}[{idx}]/{tag_name}[{after_index}]", "Type": "Show Missing", "Description": f"{elem.tag} : {elem.text}"})
            
        else:
            child_path = f"{path}/{child1.tag}[{idx}]"
            differences.extend(find_differences(child1, child2, key= key, path=child_path))

    if len(children1) > len(children2):
        for idx, child in enumerate(children1[len(children2):]):
            differences.append({"Key": key, "Path": f"{path}/{child.tag}[{len(children2)+idx}]", "Type": "Missing in after", "Description": "Element is missing"})
    elif len(children1) < len(children2):
        for idx, child in enumerate(children2[len(children1):]):
            differences.append({"Key": key, "Path": f"{path}/{child.tag}[{len(children1)+idx}]", "Type": "Missing in before", "Description": "Element is missing"})

    return differences

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