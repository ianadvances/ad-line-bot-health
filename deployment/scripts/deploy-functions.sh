#!/bin/bash

# 部署 Cloud Functions 到 Google Cloud Platform
# 此腳本打包並部署 LINE Bot Cloud Function

set -e

# 配置
FUNCTION_NAME="linebot"
REGION="asia-east1"
RUNTIME="python311"
ENTRY_POINT="linebot"
MEMORY="512MB"
TIMEOUT="540s"

# 輸出顏色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # 無顏色

echo -e "${YELLOW}🚀 部署 Cloud Functions...${NC}"

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

# 先打包函數
echo -e "${YELLOW}📦 打包函數...${NC}"
./deployment/scripts/package-functions.sh

# 部署函數
echo -e "${YELLOW}🚀 部署到 Google Cloud Functions...${NC}"
cd deployment/cloud-functions

gcloud functions deploy $FUNCTION_NAME \
    --runtime=$RUNTIME \
    --trigger=http \
    --entry-point=$ENTRY_POINT \
    --memory=$MEMORY \
    --timeout=$TIMEOUT \
    --region=$REGION \
    --allow-unauthenticated \
    --set-env-vars="PYTHONPATH=/workspace" \
    --source=.

echo -e "${GREEN}✅ Cloud Function 部署成功！${NC}"
echo -e "${GREEN}📍 函數 URL：https://$REGION-$(gcloud config get-value project).cloudfunctions.net/$FUNCTION_NAME${NC}"

# 清理
rm -f function-source.zip

echo -e "${GREEN}🎉 部署完成！${NC}"