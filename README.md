


          
# 健康諮詢 LINE BOT

## 專案概述

這是一個基於 LINE 平台的健康諮詢聊天機器人，結合了先進的自然語言處理技術和向量資料庫，能夠提供健康、醫療和飲食相關諮詢服務。機器人能夠理解用戶的問題，從知識庫中檢索相關資訊，並生成結構化的回答，同時還能推薦相關的 YouTube 影片資源。

注意：此專案僅供技術練習與學習用途，不作為實際醫療諮詢或診斷應用。

## 專案結構

```
ad-line-bot-health/
├── src/                   # 原始碼
│   ├── data_processing/   # 資料處理腳本
│   ├── apps/              # 應用程式 (LINE Bot, Streamlit)
│   └── utils/             # 工具函數
├── deployment/            # 部署配置
│   ├── cloud-functions/   # Google Cloud Functions
│   ├── cloud-run/         # Google Cloud Run
│   └── scripts/           # 部署腳本
├── data/                  # 專案資料
│   ├── audio/             # 音訊檔案
│   ├── text/              # 文字檔案
│   ├── entities/          # 實體檔案
│   └── db/                # 資料庫檔案
├── docs/                  # 文件
└── 配置檔案                
```

## 技術架構

### 核心技術

- **程式語言**：Python
- **Web 框架**：Flask (用於 Webhook)
- **雲端服務**：Google Cloud Run、Cloud Storage
- **AI 模型**：
  - Systran/faster-whisper-large-v3 (用於語音辨識)
  - DeepInfra 的 BAAI/bge-m3 (用於 Embedding)
  - OpenAI GPT-4o-mini (用於生成回應)
- **資料庫**：ChromaDB (用於語義搜尋)、DuckDB (用於對話記錄)
- **訊息平台**：LINE Messaging API

### 系統架構圖

```
用戶 <-> LINE平台 <-> Flask應用 <-> 向量資料庫(ChromaDB) <-> 知識庫
                        |
                        v
                    OpenAI API <-> GPT模型
                        |
                        v
                Google Cloud Storage <-> 對話歷史記錄
```

## 資料處理流程

### 1. 資料收集與預處理

專案包含了一系列資料處理腳本（位於 `src/data_processing/`）：
- 影片爬蟲程式 (`01_video_crawler.py`)
- 影片轉錄文本處理 (`02_transcript_to_text.py`)
- 影片轉音訊 (`03_video_to_audio.py`)
- 音訊轉文本 (`04_audio_to_text.py`)
- 資料儲存至向量資料庫 (`05_storage_chroma.py`)

這些腳本從 YouTube 健康相關頻道收集影片，提取其內容，並將其轉換為結構化的知識庫。

### 2. 向量化儲存與搜尋

所有文本資料使用 BAAI/bge-m3 模型進行向量化，並儲存在 ChromaDB 向量資料庫中，以便進行高效的語義搜尋。

Embeddings 寫入
```python
# 將長文本分割成較小的塊
text_splitter = langchain.text_splitter.RecursiveCharacterTextSplitter(
    chunk_size=6000, chunk_overlap=600, length_function=len
)
split_content = text_splitter.split_text(text)

# 初始化 ChromaDB 客戶端
client = chromadb.PersistentClient(path=str(PathHelper.db_dir))

# 創建或獲取集合
collection = client.get_or_create_collection(name=f'{channel_name}-cosine',
                                           metadata={"hnsw:space": "cosine"})

# 生成嵌入向量
model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
embeddings = model.encode(split_content, 
                         batch_size=12, 
                         max_length=8192,
                         )['dense_vecs']

# 將數據添加到集合
collection.add(
    embeddings=embeddings_list,
    documents=contents_list,
    ids=ids,
    metadatas=metadatas
)
```
Embeddings 搜尋
```python
# 生成查詢嵌入向量
def get_embedding(text: str) -> List[float]:
    embeddings = deepinfra_client.embeddings.create(
        model="BAAI/bge-m3",
        input=text,
        encoding_format="float"
    )
    return embeddings.data[0].embedding

# 配置檢索器
def configure_retriever():
    client = chromadb.PersistentClient(path='./')
    collection = client.get_collection(name=CHROMA_DB)
    return collection

# 獲取相關文檔
def get_relevant_documents(query: str, collection, top_k: int = 3) -> List[Dict]:
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"]
    )
    documents = [
        {"page_content": doc, "metadata": meta} 
        for doc, meta in zip(results['documents'][0], results['metadatas'][0])
    ]
    return documents
```

### 3. 聊天機器人實現

LINE 聊天機器人的核心功能主要包括：

- LINE 平台的訊息處理
- 用戶查詢的向量化
- 相關文檔的檢索
- 回應生成
- 對話歷史記錄管理

## 關鍵功能實現

### 1. 語義搜尋

當用戶提出問題時，系統會將問題轉換為向量表示，然後在向量資料庫中搜尋最相關的文檔：

```python
def get_relevant_documents(query: str, collection, top_k: int = 3) -> List[Dict]:
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"]
    )
    documents = [
        {"page_content": doc, "metadata": meta} 
        for doc, meta in zip(results['documents'][0], results['metadatas'][0])
    ]
    return documents
```

### 2. 上下文感知回應生成

系統會考慮用戶的當前問題、對話歷史以及從知識庫中檢索到的相關資訊，生成連貫且有上下文感知的回應：

```python
messages_for_ai = [
    {"role": "system", "content": f"你是一位專業的健康、醫療和飲食相關的諮詢師。用繁體中文回覆。可以參考以下背景資訊但不限於此來回答問題:\n\n{context}\n除了以上資訊你可以再進行補充，回答不用過長，回答得有結構及完整就好。必要時可以跟使用者詢問更多資訊來提供給你。"},
    {"role": "user", "content": f"之前的對話紀錄：\n{chat_history}\n\n使用者的最新問題：{user_input}"}
]
```

### 3. 對話歷史管理

系統使用 DuckDB 在 Google Cloud Storage 儲存對話歷史，並在生成回應時考慮最近的對話內容，以提供更連貫的用戶體驗：

```python
def log_message_to_gcs(user_input, llm_output, chat_room_id, blob):
    taipei_time = datetime.now(timezone.utc) + timedelta(hours=8)
    
    new_row = {
        "timestamp": taipei_time.strftime('%Y-%m-%d %H:%M:%S'),
        "chat_room_id": chat_room_id,
        "user_input": user_input,
        "llm_output": llm_output
    }
    
    # ... 儲存對話記錄的邏輯 ...
```

### 4. 多媒體資源推薦

系統不僅提供文字回應，還能根據用戶的問題推薦相關的 YouTube 影片：

```python
# 添加 YouTube URL 到回覆中
youtube_urls = []
for doc in relevant_docs:
    if 'video_id' in doc['metadata']:
        video_id = doc['metadata']['video_id']
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        youtube_urls.append(youtube_url)

if youtube_urls:
    llm_output += "\n\n推薦影片：\n" + "\n".join(youtube_urls)
```

## 技術亮點

### 1. 檢索增強生成 (RAG) 架構

專案採用了 RAG (Retrieval-Augmented Generation) 架構，結合了向量資料庫的檢索能力和大型語言模型的生成能力，提供準確且有深度的回應。

### 2. 多模態資訊整合

系統能夠整合文本和視頻資源，為用戶提供更全面的健康資訊。通過推薦相關的 YouTube 影片，用戶可以獲得更直觀的健康知識。

### 3. 上下文感知對話

通過儲存和利用對話歷史，系統能夠維持連貫的對話流程，理解用戶在對話中的上下文，提供更自然的互動體驗。

### 4. 可擴展的知識庫

專案的知識庫設計允許持續添加新的健康資訊，使系統能夠不斷學習和更新其知識庫，保持資訊的時效性和準確性。

## 部署與擴展

### 部署環境

系統設計為在雲端環境中運行，支援：
- **Google Cloud Functions**: 無伺服器函數部署
- **Google Cloud Run**: 容器化應用程式部署
- **本地開發**: 使用 Flask 開發伺服器

### 擴展性考慮

1. **知識庫擴展**：可以持續添加新的健康資訊來源，如醫學期刊、健康網站等
2. **多語言支持**：當前系統使用繁體中文，但架構允許輕鬆擴展到其他語言
3. **多平台整合**：除了 LINE，系統架構允許整合到其他訊息平台，如 Telegram、Discord 等

## 結論

這個健康諮詢 LINE 聊天機器人專案展示了如何結合現代 AI 技術和雲端服務，創建一個實用的健康資訊助手。通過語義搜尋、上下文感知對話和多媒體資源推薦，系統能夠提供個性化且專業的健康諮詢服務，幫助用戶獲取相關健康資訊。

專案的模組化設計和可擴展架構使其具有很高的適應性和成長潛力，能夠隨著技術的發展和用戶需求的變化而不斷進化。


## 附件：
聊天畫面
<img style="display:block;margin:20px auto;padding:1px;border:1px #eee;width:60%;" src="https://hackmd.io/_uploads/H1WaFWMlel.jpg" />

