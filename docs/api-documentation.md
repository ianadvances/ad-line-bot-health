# API 文件

## 概述

本文件提供 ad-line-bot-health 專案的完整 API 參考，包括 LINE Bot webhook、Streamlit 應用程式端點和內部服務 API。

## LINE Bot API

### Webhook 端點

**端點：** `POST /webhook`

**說明：** 接收來自 LINE 平台的訊息和事件

#### 請求標頭

```
Content-Type: application/json
X-Line-Signature: {signature}
```

#### 請求內容

```json
{
  "destination": "string",
  "events": [
    {
      "type": "message",
      "mode": "active",
      "timestamp": 1234567890123,
      "source": {
        "type": "user",
        "userId": "string"
      },
      "webhookEventId": "string",
      "deliveryContext": {
        "isRedelivery": false
      },
      "message": {
        "id": "string",
        "type": "text",
        "quoteToken": "string",
        "text": "string"
      },
      "replyToken": "string"
    }
  ]
}
```

#### 回應

```json
{
  "status": "success",
  "message": "事件處理成功"
}
```

#### 錯誤回應

```json
{
  "status": "error",
  "message": "無效簽章",
  "code": 400
}
```

### 支援的訊息類型

#### 文字訊息

- **輸入：** 純文字查詢
- **處理：** ChromaDB 相似度搜尋
- **輸出：** 相關健康資訊回應

#### 快速回覆訊息

- **分類：** 健康諮詢, 運動建議, 營養資訊
- **回應：** 分類特定資訊

## Streamlit 網頁應用程式 API

### 健康檢查端點

**端點：** `GET /health`

**說明：** 應用程式健康狀態

#### 回應

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

### 搜尋端點

**端點：** `POST /api/search`

**說明：** 搜尋健康資訊

#### 請求內容

```json
{
  "query": "string",
  "limit": 10,
  "threshold": 0.7
}
```

#### 回應

```json
{
  "results": [
    {
      "id": "string",
      "content": "string",
      "metadata": {
        "source": "string",
        "timestamp": "string",
        "category": "string"
      },
      "similarity_score": 0.85
    }
  ],
  "total_results": 1,
  "query_time": 0.123
}
```

## 內部服務 API

### 資料處理服務

#### 影片爬蟲服務

**模組：** `src.data_processing.01_video_crawler`

**函數：**

```python
def crawl_videos(channel_id: str, max_videos: int = 100) -> List[Dict]:
    """
    從 YouTube 頻道爬取影片
    
    參數：
        channel_id: YouTube 頻道 ID
        max_videos: 要爬取的最大影片數量
        
    回傳：
        影片元資料字典列表
    """
```

#### 轉錄處理服務

**模組：** `src.data_processing.02_transcript_to_text`

**函數：**

```python
def process_transcript(video_id: str) -> Dict:
    """
    處理影片轉錄為文字
    
    參數：
        video_id: YouTube 影片 ID
        
    回傳：
        處理後的轉錄資料
    """
```

#### 音訊處理服務

**模組：** `src.data_processing.03_video_to_audio`

**函數：**

```python
def extract_audio(video_path: str, output_path: str) -> bool:
    """
    從影片檔案提取音訊
    
    參數：
        video_path: 影片檔案路徑
        output_path: 輸出音訊檔案路徑
        
    回傳：
        成功狀態
    """
```

#### 語音轉文字服務

**模組：** `src.data_processing.04_audio_to_text`

**函數：**

```python
def transcribe_audio(audio_path: str) -> Dict:
    """
    將音訊轉錄為文字
    
    參數：
        audio_path: 音訊檔案路徑
        
    回傳：
        包含元資料的轉錄結果
    """
```

#### ChromaDB 儲存服務

**模組：** `src.data_processing.05_storage_chroma`

**函數：**

```python
def store_documents(documents: List[Dict]) -> bool:
    """
    將文件儲存到 ChromaDB
    
    參數：
        documents: 文件字典列表
        
    回傳：
        成功狀態
    """

def search_similar(query: str, limit: int = 10) -> List[Dict]:
    """
    搜尋相似文件
    
    參數：
        query: 搜尋查詢
        limit: 回傳的最大結果數
        
    回傳：
        相似文件列表
    """
```

### 工具服務

#### 日誌記錄服務

**模組：** `src.utils.logger`

**函數：**

```python
def get_logger(name: str) -> logging.Logger:
    """
    取得已配置的日誌記錄器實例
    
    參數：
        name: 日誌記錄器名稱（通常是 __name__）
        
    回傳：
        已配置的日誌記錄器實例
    """
```

#### 路徑輔助服務

**模組：** `src.utils.path_helper`

**函數：**

```python
def get_data_path(filename: str) -> str:
    """
    取得資料檔案的絕對路徑
    
    參數：
        filename: 資料檔案名稱
        
    回傳：
        絕對檔案路徑
    """

def ensure_directory(path: str) -> bool:
    """
    確保目錄存在
    
    參數：
        path: 目錄路徑
        
    回傳：
        成功狀態
    """
```

## 資料庫 API

### ChromaDB 操作

#### 集合管理

```python
# 建立集合
collection = client.create_collection(
    name="health_documents",
    metadata={"description": "健康資訊文件"}
)

# 取得集合
collection = client.get_collection(name="health_documents")
```

#### 文件操作

```python
# 新增文件
collection.add(
    documents=["文件內容"],
    metadatas=[{"source": "video_id", "timestamp": "2024-01-01"}],
    ids=["doc_1"]
)

# 查詢文件
results = collection.query(
    query_texts=["健康查詢"],
    n_results=10,
    where={"source": {"$eq": "specific_video"}}
)
```

## 錯誤處理

### 標準錯誤回應格式

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "人類可讀的錯誤訊息",
    "details": {
      "field": "額外錯誤詳情"
    },
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### 常見錯誤代碼

| 代碼 | 說明 | HTTP 狀態 |
|------|-------------|-------------|
| `INVALID_REQUEST` | 請求驗證失敗 | 400 |
| `UNAUTHORIZED` | 需要身份驗證 | 401 |
| `FORBIDDEN` | 存取被拒絕 | 403 |
| `NOT_FOUND` | 找不到資源 | 404 |
| `RATE_LIMITED` | 請求過多 | 429 |
| `INTERNAL_ERROR` | 伺服器錯誤 | 500 |
| `SERVICE_UNAVAILABLE` | 服務暫時無法使用 | 503 |

### LINE Bot 特定錯誤

| 代碼 | 說明 |
|------|-------------|
| `INVALID_SIGNATURE` | LINE 簽章驗證失敗 |
| `UNSUPPORTED_EVENT` | 不支援的事件類型 |
| `MESSAGE_TOO_LONG` | 回應訊息超過限制 |
| `USER_BLOCKED` | 使用者已封鎖機器人 |

## 速率限制

### LINE Bot API 限制

- **每秒訊息數：** 100
- **每分鐘訊息數：** 1,000
- **每小時訊息數：** 10,000

### 內部 API 限制

- **每分鐘搜尋請求：** 60
- **每小時資料處理請求：** 100

## 身份驗證

### LINE Bot Webhook 驗證

```python
def verify_signature(body: bytes, signature: str) -> bool:
    """
    驗證 LINE webhook 簽章
    
    參數：
        body: 請求內容位元組
        signature: X-Line-Signature 標頭值
        
    回傳：
        驗證結果
    """
```

### API 金鑰身份驗證

對於需要身份驗證的內部 API：

```http
Authorization: Bearer YOUR_API_KEY
```

## 資料模型

### 文件模型

```python
class Document:
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float]
    created_at: datetime
    updated_at: datetime
```

### 搜尋結果模型

```python
class SearchResult:
    document: Document
    similarity_score: float
    rank: int
```

### 使用者訊息模型

```python
class UserMessage:
    user_id: str
    message_text: str
    timestamp: datetime
    message_type: str
    reply_token: str
```

## 配置

### 環境變數

| 變數 | 說明 | 必要 | 預設值 |
|----------|-------------|----------|----------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot 存取權杖 | 是 | - |
| `LINE_CHANNEL_SECRET` | LINE Bot 頻道密鑰 | 是 | - |
| `DEEPINFRA_API_KEY` | DeepInfra API 金鑰 | 是 | - |
| `CHROMA_DB_PATH` | ChromaDB 資料庫路徑 | 否 | `./data/db/chroma.sqlite3` |
| `MAX_RESPONSE_LENGTH` | 最大回應長度 | 否 | `2000` |
| `SEARCH_THRESHOLD` | 相似度搜尋閾值 | 否 | `0.7` |
| `LOG_LEVEL` | 日誌記錄等級 | 否 | `INFO` |

### 應用程式設定

```python
class Settings:
    line_channel_access_token: str
    line_channel_secret: str
    deepinfra_api_key: str
    chroma_db_path: str = "./data/db/chroma.sqlite3"
    max_response_length: int = 2000
    search_threshold: float = 0.7
    log_level: str = "INFO"
```

## 範例

### LINE Bot 訊息處理

```python
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextMessage, TextSendMessage

def handle_text_message(event):
    user_message = event.message.text
    
    # 搜尋相關資訊
    results = search_similar(user_message, limit=3)
    
    # 格式化回應
    response_text = format_search_results(results)
    
    # 發送回覆
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_text)
    )
```

### Streamlit 搜尋介面

```python
import streamlit as st

def search_interface():
    query = st.text_input("輸入健康相關問題:")
    
    if st.button("搜尋"):
        results = search_similar(query)
        
        for result in results:
            st.write(f"**相似度:** {result['similarity_score']:.2f}")
            st.write(result['content'])
            st.write("---")
```

### ChromaDB 整合

```python
import chromadb

def initialize_database():
    client = chromadb.PersistentClient(path="./data/db")
    
    collection = client.get_or_create_collection(
        name="health_documents",
        metadata={"description": "健康資訊集合"}
    )
    
    return collection

def add_document(collection, doc_id, content, metadata):
    collection.add(
        documents=[content],
        metadatas=[metadata],
        ids=[doc_id]
    )
```

## 測試

### API 測試範例

```python
import requests

# 測試 LINE webhook
def test_webhook():
    payload = {
        "events": [{
            "type": "message",
            "message": {"type": "text", "text": "健康問題"},
            "replyToken": "test_token"
        }]
    }
    
    response = requests.post(
        "http://localhost:5000/webhook",
        json=payload,
        headers={"X-Line-Signature": "test_signature"}
    )
    
    assert response.status_code == 200

# 測試搜尋功能
def test_search():
    results = search_similar("運動建議", limit=5)
    assert len(results) <= 5
    assert all("similarity_score" in result for result in results)
```

## 監控和指標

### 關鍵指標

- **回應時間：** 平均 API 回應時間
- **成功率：** 成功請求的百分比
- **錯誤率：** 失敗請求的百分比
- **資料庫查詢時間：** ChromaDB 查詢效能
- **使用者參與度：** 訊息量和模式

### 健康檢查端點

```python
@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "database": check_database_connection(),
        "timestamp": datetime.utcnow().isoformat()
    }
```