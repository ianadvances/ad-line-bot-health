#!/bin/bash

# 部署 Cloud Run 服務到 Google Cloud Platform
# 此腳本建置並部署 LINE Bot 容器化應用程式

set -e

# 配置
SERVICE_NAME="line-bot-health"
REGION="asia-east1"
PLATFORM="managed"
MEMORY="1Gi"
CPU="1"
MAX_INSTANCES="10"
PORT="8080"

# 輸出顏色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # 無顏色

echo -e "${YELLOW}🚀 部署到 Cloud Run...${NC}"

# 檢查是否已安裝 gcloud
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ 未安裝 gcloud CLI。請先安裝。${NC}"
    exit 1
fi

# 檢查使用者是否已驗證
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ 未通過 gcloud 驗證。請執行 'gcloud auth login'${NC}"
    exit 1
fi

# 取得專案 ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ 未設定專案。請執行 'gcloud config set project PROJECT_ID'${NC}"
    exit 1
fi

# 使用 Cloud Build 建置和部署
echo -e "${YELLOW}🏗️  使用 Cloud Build 建置和部署...${NC}"
cd deployment/cloud-run

gcloud run deploy $SERVICE_NAME \
    --source=. \
    --platform=$PLATFORM \
    --region=$REGION \
    --memory=$MEMORY \
    --cpu=$CPU \
    --max-instances=$MAX_INSTANCES \
    --port=$PORT \
    --allow-unauthenticated \
    --set-env-vars="PORT=$PORT"

echo -e "${GREEN}✅ Cloud Run 服務部署成功！${NC}"

# 取得服務 URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo -e "${GREEN}📍 服務 URL：$SERVICE_URL${NC}"
echo -e "${GREEN}🔗 Webhook URL：$SERVICE_URL/callback${NC}"

echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${YELLOW}📝 別忘了更新您的 LINE Bot webhook URL 為：$SERVICE_URL/callback${NC}"