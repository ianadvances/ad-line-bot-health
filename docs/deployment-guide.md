# 部署指南

## 概述

本指南涵蓋 ad-line-bot-health 專案的部署程序，支援 Google Cloud Functions 和 Google Cloud Run 部署。

## 先決條件

- 已安裝並配置 Google Cloud SDK
- 已安裝 Docker（用於 Cloud Run 部署）
- 已安裝 Python 3.8+
- 具有適當權限的 Google Cloud 專案存取權

## 部署前測試

**建議在部署前使用 Streamlit 應用程式進行本地測試**：

```bash
# 確保所有依賴套件已安裝
pip install -r requirements.txt

# 配置環境變數
cp .env.example .env
# 編輯 .env 檔案，填入必要的 API 金鑰

# 執行本地測試
cd src/apps
streamlit run 06_app_streamlit.py
```

這將驗證：
- 所有 API 金鑰配置正確
- ChromaDB 資料庫可正常存取
- 嵌入和聊天模型正常運作
- 整體系統功能完整性

## 環境設定

1. **配置 Google Cloud CLI**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **設定環境變數**
   複製 `.env.example` 到 `.env` 並配置：
   ```bash
   cp .env.example .env
   # 編輯 .env 檔案，填入您的特定值
   ```

## Google Cloud Functions 部署

### 手動部署

1. **導航到 Functions 目錄**
   ```bash
   cd deployment/cloud-functions
   ```

2. **部署函數**
   ```bash
   gcloud functions deploy YOUR_FUNCTION_NAME \
     --runtime python38 \
     --trigger-http \
     --allow-unauthenticated \
     --source .
   ```

### 自動化部署

使用提供的部署腳本：
```bash
cd deployment/scripts
./deploy-functions.sh
```

### 函數配置

- **執行環境**: Python 3.8
- **記憶體**: 512MB（可根據需求調整）
- **逾時**: 540 秒
- **觸發器**: HTTP

## Google Cloud Run 部署

### 手動部署

1. **建置容器映像**
   ```bash
   cd deployment/cloud-run
   docker build -t gcr.io/YOUR_PROJECT_ID/line-bot-health .
   ```

2. **推送到容器註冊表**
   ```bash
   docker push gcr.io/YOUR_PROJECT_ID/line-bot-health
   ```

3. **部署到 Cloud Run**
   ```bash
   gcloud run deploy line-bot-health \
     --image gcr.io/YOUR_PROJECT_ID/line-bot-health \
     --platform managed \
     --region asia-east1 \
     --allow-unauthenticated
   ```

### 自動化部署

使用提供的部署腳本：
```bash
cd deployment/scripts
./deploy-cloud-run.sh
```

### 容器配置

- **基礎映像**: python:3.8-slim
- **連接埠**: 8080
- **健康檢查**: `/health` 端點
- **記憶體**: 1Gi
- **CPU**: 1000m

## 資料庫設定

### ChromaDB 配置

1. **本地開發**
   - 資料庫檔案儲存在 `data/db/` 中
   - 首次執行時自動初始化

2. **正式環境部署**
   - 資料庫檔案包含在部署套件中
   - 確保適當的備份程序

## 環境變數

### 必要變數

```env
# LINE Bot 配置
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret

# API 金鑰
DEEPINFRA_API_KEY=your_deepinfra_api_key

# 資料庫配置
CHROMA_DB_PATH=./data/db/chroma.sqlite3

# 應用程式設定
DEBUG=false
LOG_LEVEL=INFO
```

### 可選變數

```env
# 自訂配置
MAX_RESPONSE_LENGTH=2000
DEFAULT_LANGUAGE=zh-TW
```

## 監控和日誌記錄

### Cloud Functions 監控

- 查看日誌：`gcloud functions logs read YOUR_FUNCTION_NAME`
- 在 Google Cloud Console 中監控指標
- 設定錯誤和效能警報

### Cloud Run 監控

- 查看日誌：`gcloud run services logs YOUR_SERVICE_NAME`
- 監控容器指標
- 配置健康檢查和自動擴展

## 疑難排解

### 常見問題

1. **匯入路徑錯誤**
   - 確保所有 Python 匯入使用絕對路徑
   - 驗證 requirements.txt 包含所有依賴套件

2. **資料庫連線問題**
   - 檢查資料庫檔案權限
   - 驗證 ChromaDB 初始化

3. **記憶體限制**
   - 為大型資料集增加記憶體配置
   - 最佳化資料處理以提高記憶體效率

4. **逾時問題**
   - 為長時間執行的操作增加函數逾時
   - 考慮將大型操作分解為較小的區塊

### 除錯指令

```bash
# 測試本地函數
functions-framework --target=main --debug

# 在本地測試容器
docker run -p 8080:8080 gcr.io/YOUR_PROJECT_ID/line-bot-health

# 檢查部署狀態
gcloud functions describe YOUR_FUNCTION_NAME
gcloud run services describe YOUR_SERVICE_NAME
```

## 安全考量

1. **環境變數**
   - 絕不將 `.env` 檔案提交到版本控制
   - 使用 Google Secret Manager 處理敏感資料

2. **存取控制**
   - 配置適當的 IAM 角色
   - 使用最小權限原則

3. **網路安全**
   - 如需要，配置 VPC
   - 對所有端點使用 HTTPS

## 備份和復原

1. **資料庫備份**
   - 定期備份 ChromaDB 檔案
   - 將備份儲存在 Google Cloud Storage 中

2. **配置備份**
   - 版本控制所有配置檔案
   - 記錄環境特定設定

## 效能最佳化

1. **冷啟動減少**
   - 使用排程請求保持函數溫暖
   - 最佳化匯入陳述式

2. **記憶體使用量**
   - 定期分析記憶體使用量
   - 最佳化資料結構和演算法

3. **回應時間**
   - 快取經常存取的資料
   - 在可能的地方使用非同步操作