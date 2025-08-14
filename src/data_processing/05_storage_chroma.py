channel_name = 'Cofit211'

import os
import pandas as pd
# from openai import OpenAI
from FlagEmbedding import BGEM3FlagModel
from dotenv import load_dotenv
from langchain.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
import chromadb
import time

try:
    import sys
    from pathlib import Path
    
    # 將專案根目錄加入 Python 路徑以供匯入
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from src.utils import PathHelper, get_logger
except Exception as e:
    print(e)
    raise Exception("Please run this script from the root directory of the project")

# 日誌記錄器
logger = get_logger(__name__)

# 載入環境變數
dotenv_path = PathHelper.root_dir / ".env"
load_dotenv(dotenv_path=dotenv_path)

# # Initialize OpenAI client
# openai = OpenAI(
#     api_key=os.getenv("DEEPINFRA_API_KEY"),
#     base_url="https://api.deepinfra.com/v1/openai",
# )

def main():
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=6000, chunk_overlap=600, length_function=len
    )
    
    # 載入資料到資料框
    videos = os.listdir(PathHelper.text_dir / channel_name)
    video_ids = [v.split(".")[0] for v in videos]
    df_videos = pd.DataFrame({"video_id": video_ids})
    
    # 初始化 Chroma 客戶端
    client = chromadb.PersistentClient(path=str(PathHelper.db_dir))

    # 檢查集合是否存在，如果不存在則建立
    try:
        collection = client.get_or_create_collection(name=channel_name+'-cosine',
                                                     metadata={"hnsw:space": "cosine"})
        print(f"Using collection '{channel_name}'.")
    except ValueError as e:
        print(f"Error creating or getting collection: {e}")
        raise

    new_list = []
    # 透過將文字分割為約 8192 個 token 的大小來建立新清單
    for _, row in df_videos.iterrows():
        video_id = row["video_id"]
        
        # 檢查 video_id 是否已存在於集合中
        existing_docs = collection.get(
            where={"video_id": video_id},
            include=["metadatas"]
        )
        
        if existing_docs["ids"]:
            print(f"Video ID {video_id} already exists in the collection. Skipping.")
            continue
        
        try:
            with open(PathHelper.text_dir / channel_name / f"{video_id}.txt", encoding="utf8") as f:
                transcript = f.readlines()
                text = eval(transcript[0])
            print(f"{video_id} length: {len(text)}")
            
            if len(text) <= 6000:
                new_list.append([video_id, text, 0])
            else:
                # 使用文字分割器將文字分割為塊
                split_text = text_splitter.split_text(text)
                for j, chunk in enumerate(split_text):
                    new_list.append([video_id, chunk, j])
                    
        except Exception as e:
            logger.error(f"Error processing video ID {video_id}: {e}")
    
    if not new_list:
        print("No new videos to process. Exiting.")
        return client

    df_new = pd.DataFrame(new_list, columns=["video_id", "content", "chunk_index"])
    
    # 建立文件
    loader = DataFrameLoader(df_new, page_content_column="content")
    docs = loader.load()
    page_contents = [doc.page_content for doc in docs]
    embeddings_list = []
    
    # 建立嵌入向量 
    model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
    for content in tqdm(page_contents, total=len(page_contents)):
    # for content in page_contents:
        t1 = time.time()
        # embeddings = openai.embeddings.create(
        #     model="BAAI/bge-m3",
        #     input=content,
        #     encoding_format="float"
        # )
        embeddings = model.encode(content, 
                                  batch_size=12, 
                                  max_length=8192,
                                  )['dense_vecs']
        t2 = time.time()
        print(f"len(str): {len(content)}")
        # print(f"Tokens used for embedding: {embeddings.usage.prompt_tokens}")
        print(f"Sec used: {t2 - t1}")
        print("==================================")
        # embeddings_list.append(embeddings.data[0].embedding)
        embeddings_list.append(embeddings.tolist())

    # 準備資料
    # 修改 ids 的產生方式，確保唯一性
    ids = [f"id_{row['video_id']}_{row['chunk_index']}" for _, row in df_new.iterrows()]
    # 只在 metadatas 中包含 video_id
    metadatas = [{"video_id": row['video_id']} for _, row in df_new.iterrows()]

    # 將資料加入集合
    collection.add(
        embeddings=embeddings_list,
        documents=page_contents,
        ids=ids,
        metadatas=metadatas
    )

    print(f"Added {len(new_list)} new video chunks to the collection.")
    return client

if __name__ == "__main__":
    main()