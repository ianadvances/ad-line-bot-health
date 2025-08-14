#!/bin/bash

# 打包 Cloud Functions 以供部署
# 基於原始 zip_command.txt 需求

set -e

echo "📦 打包 Cloud Functions 以供部署..."

# 切換到 cloud functions 目錄
cd deployment/cloud-functions

# 移除任何 .DS_Store 檔案
find . -name ".DS_Store" -type f -delete

# 建立部署套件
echo "建立 function-source.zip..."
zip -r function-source.zip \
    main.py \
    requirements.txt \
    chroma.sqlite3 \
    b67cd040-1701-467f-b8cb-a6b369b398b0/

echo "✅ Cloud Functions 套件已建立：deployment/cloud-functions/function-source.zip"
echo "📁 套件內容："
unzip -l function-source.zip

echo ""
echo "🚀 準備部署到 Google Cloud Functions！"
echo "   使用：gcloud functions deploy [FUNCTION_NAME] --source=deployment/cloud-functions/function-source.zip"