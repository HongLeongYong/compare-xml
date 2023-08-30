# 大 XML 分割與比對工具

本 repository 提供一套工具，用於將大型 XML 檔案拆分成較小的片段，並進行資料比對。

## 目錄

- [安裝](#安裝)
- [使用方法](#使用方法)
  - [設定全局變數](#1-設定全局變數)
  - [檔名調整](#2-檔名調整)
  - [XML 拆分](#3-xml-拆分)
  - [找出差異](#4-找出差異)
  - [XML 比對](#5-xml-比對)

## 安裝

請將本 repository 克隆到本地端，並確保 Python 環境已正確設置。

```bash
git clone https://github.com/your_username/your_repository.git
```

## 使用方法 🛠️

### 1. 設定全局變數 🌍

- **檔案**: `global_variable.py`

  您需要指定以下三個路徑：
  1. 🗂️ 大 XML 檔案的存放位置。
  2. 📦 分割後的 XML 檔案存放位置。
  3. 🎯 比對結果的存放位置。

### 2. 檔名調整 📝

- **使用腳本**: `01 change file name.py`

  📌 如果您的大型 XML 檔案沒有 `.xml` 擴展名，這個腳本可以幫您自動添加。

### 3. XML 拆分 📤📥 [code](02_split_xml_file.py)

- **使用腳本**: `02_split_xml_file.py`

  ✂️ 此腳本會將大型 XML 檔案拆分成多個較小的片段。

### 4. 找出差異 🔍

- **使用腳本**: `03 get different file.py`

  🕵️ 此腳本會比對 "before" 和 "after" 資料夾中的檔案，並找出不同。

  > **註**: 📤 如果您設置 `move_file_boolean = True`，腳本會將不同的檔案移動到指定的資料夾。

### 5. XML 比對 📊

- **使用腳本**: `04 compare_xml.py`

  🔄 這個腳本會對拆分後的 XML 進行資料比對。您可能需要根據您的需要調整 `def reprocess_string()` 函數。

## 貢獻 

如果您有任何建議或問題，📬 請開啟一個 issue 或提交一個 pull request。

## 授權

🔒 本項目使用 [MIT License](LICENSE).

