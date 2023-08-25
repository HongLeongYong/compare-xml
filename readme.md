# 使用方法  
本 respository 適合用於把大xml分割成小xml，然後進行**比對**  

## 1. 更新 global_variable.py  
需指定  
1. 大 xml 檔案路徑  
2. 分割後的 xml 檔案路徑  
3. 結果檔案路徑  

## 2. 加入 file type  
使用 `01 change file name.py`  
有時 大xml 在結尾沒(.xml), 這程式能加 file type(.xml)  

## 3. 大xml 拆分成 小xml  
使用 `02 split xml file.py`
大xml 拆分成 n個小xml  

## 4. 找出 before & after 的差異檔案  
使用 `03 get different file.py`  
找出 before 資料夾 和 after 資料夾中 檔案的不同  
如果設定 `move_file_boolean = True`, 有移動不同檔案到指定資料夾功能  

## 5. 對比 xml 資料💾  
使用 `04 compare_xml.py`  
需自行調整 `def reprocess_string()`  
