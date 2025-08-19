# 開發環境設定指南

## 概述

本指南將協助您為 ad-line-bot-health 專案設定本地開發環境。

## 先決條件

- Python 3.8 或更高版本
- Git
- Google Cloud SDK（可選，用於雲端服務）
- Docker（可選，用於容器化開發）

## 初始設定

### 1. 複製儲存庫

```bash
git clone <repository-url>
cd ad-line-bot-health
```

### 2. 建立虛擬環境

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# 在 macOS/Linux：
source venv/bin/activate
# 在 Windows：
venv\Scripts\activate
```

### 3. 安裝依賴套件

```bash
# 安裝主要專案依賴套件
pip install -r requirements.txt

# 用於開發的額外工具
pip install -r requirements.txt pytest black flake8
```

### 4. 環境配置

```bash
# 複製環境範本
cp .env.example .env

# 編輯 .env 檔案進行配置
# 必要變數：
# - LINE_CHANNEL_ACCESS_TOKEN
# - LINE_CHANNEL_SECRET  
# - DEEPINFRA_API_KEY
```

## 專案結構

```
ad-line-bot-health/
├── src/                    # 原始碼
│   ├── data_processing/    # 資料處理腳本
│   ├── apps/               # 應用程式（LINE bot、Streamlit）
│   └── utils/              # 工具函數
├── deployment/             # 部署配置
│   ├── cloud-functions/    # Google Cloud Functions
│   ├── cloud-run/          # Google Cloud Run
│   └── scripts/            # 部署腳本
├── data/                   # 資料檔案
│   ├── audio/              # 音訊檔案
│   ├── text/               # 文字檔案
│   ├── entities/           # 實體檔案
│   └── db/                 # 資料庫檔案
├── docs/                   # 文件
└── requirements.txt        # Python 依賴套件
```

## 開發工作流程

### 1. 資料處理管線

資料處理管線包含數個應按順序執行的腳本：

```bash
# 導航到原始碼目錄
cd src

# 1. 影片爬取（如需要）
python data_processing/01_video_crawler.py

# 2. 轉錄文字轉換
python data_processing/02_transcript_to_text.py

# 3. 影片轉音訊
python data_processing/03_video_to_audio.py

# 4. 音訊轉文字
python data_processing/04_audio_to_text.py

# 5. 儲存到 ChromaDB
python data_processing/05_storage_chroma.py
```

### 2. 執行應用程式

#### LINE Bot 應用程式

```bash
cd src/apps
python 06_app_linebot.py
```

#### Streamlit 網頁應用程式

```bash
cd src/apps
streamlit run 06_app_streamlit.py
```

### 3. 資料庫管理

#### 檢查資料庫狀態

```bash
cd src
python check_db.py
```

#### 讀取文字檔案

```bash
cd src
python read_txt.py
```

## 開發工具

### 程式碼格式化

```bash
# 使用 black 格式化程式碼
black src/

# 使用 flake8 檢查程式碼風格
flake8 src/
```

### 測試

```bash
# 執行測試（如果測試檔案存在）
pytest tests/

# 執行特定測試檔案
pytest tests/test_specific.py
```

### 除錯

#### 啟用除錯模式

在您的 `.env` 檔案中設定：
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

#### 日誌記錄配置

專案使用結構化日誌記錄。日誌在 `src/utils/logger.py` 中配置：

```python
import logging
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("除錯訊息")
```

## 資料庫設定

### ChromaDB 本地設定

1. **自動初始化**
   - ChromaDB 將在首次執行時自動初始化
   - 資料庫檔案儲存在 `data/db/` 中

2. **手動重置資料庫**
   ```bash
   # 移除現有資料庫
   rm -rf data/db/*
   
   # 透過執行儲存腳本重新初始化
   cd src
   python data_processing/05_storage_chroma.py
   ```

## API 開發

### LINE Bot Webhook

1. **使用 ngrok 進行本地開發**
   ```bash
   # 安裝 ngrok
   # 在本地啟動您的 LINE bot
   python src/apps/06_app_linebot.py
   
   # 在另一個終端機中，公開本地伺服器
   ngrok http 5000
   
   # 使用 ngrok URL 更新 LINE webhook URL
   ```

2. **Webhook 測試**
   ```bash
   # 測試 webhook 端點
   curl -X POST http://localhost:5000/webhook \
     -H "Content-Type: application/json" \
     -d '{"events": []}'
   ```

### Streamlit 開發

```bash
# 使用自動重新載入執行
streamlit run src/apps/06_app_streamlit.py --server.runOnSave true

# 在特定連接埠執行
streamlit run src/apps/06_app_streamlit.py --server.port 8501
```

## 環境變數參考

### 必要變數

```env
# LINE Bot 配置
LINE_CHANNEL_ACCESS_TOKEN=your_access_token
LINE_CHANNEL_SECRET=your_channel_secret

# API 金鑰
DEEPINFRA_API_KEY=your_api_key

# 資料庫
CHROMA_DB_PATH=./data/db/chroma.sqlite3
```

### 開發變數

```env
# 除錯設定
DEBUG=true
LOG_LEVEL=DEBUG

# 開發連接埠
FLASK_PORT=5000
STREAMLIT_PORT=8501

# 本地路徑
AUDIO_PATH=./data/audio
TEXT_PATH=./data/text
ENTITIES_PATH=./data/entities
```

## 常見開發任務

### 新增資料處理腳本

1. 在 `src/data_processing/` 中建立新腳本
2. 遵循命名慣例：`##_description.py`
3. 從 `src.utils` 匯入工具
4. 新增日誌記錄和錯誤處理
5. 更新文件

### 新增應用程式

1. 在 `src/apps/` 中建立新應用程式
2. 遵循命名慣例：`##_app_name.py`
3. 配置環境變數
4. 如需要，新增到部署配置中

### 修改工具

1. 編輯 `src/utils/` 中的檔案
2. 確保向後相容性
3. 更新相依檔案中的匯入
4. 在所有應用程式中測試

## 疑難排解

### 常見問題

1. **匯入錯誤**
   ```bash
   # 確保您在專案根目錄中
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **資料庫連線問題**
   ```bash
   # 檢查資料庫檔案權限
   ls -la data/db/
   
   # 重新初始化資料庫
   python src/data_processing/05_storage_chroma.py
   ```

3. **缺少依賴套件**
   ```bash
   # 重新安裝需求
   pip install -r requirements.txt --force-reinstall
   ```

4. **環境變數問題**
   ```bash
   # 檢查 .env 是否已載入
   python -c "import os; print(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))"
   ```

### 除錯指令

```bash
# 檢查 Python 路徑
python -c "import sys; print(sys.path)"

# 測試匯入
python -c "from src.utils.logger import get_logger; print('匯入成功')"

# 檢查 ChromaDB
python -c "import chromadb; print('ChromaDB 可用')"

# 測試 LINE Bot 配置
python -c "from linebot import LineBotApi; print('LINE Bot SDK 可用')"
```
