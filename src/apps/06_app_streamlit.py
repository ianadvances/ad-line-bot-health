import os
import streamlit as st
from dotenv import load_dotenv
from FlagEmbedding import BGEM3FlagModel
import chromadb
from openai import OpenAI
from typing import List, Dict
import sys
from pathlib import Path

# 將專案根目錄加入 Python 路徑以供匯入
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils import PathHelper, get_logger

# 常數定義
CHANNEL_NAME = 'Cofit211'
CHROMA_DB = 'Cofit211-cosine'
CHAT_MODEL_NAME = "gpt-4o-mini"
INIT_MESSAGE = "您好!我是您的 AI 諮詢師。有什麼我可以幫您的嗎?"

# 設定日誌
logger = get_logger(__name__)

# 載入環境變數
dotenv_path = PathHelper.root_dir / ".env"
load_dotenv(dotenv_path=dotenv_path)

st.set_page_config(page_title="AI 保健室", page_icon="🧑‍⚕️")
st.title("👨🏻‍⚕️ AI 保健室 🧑🏻‍⚕️")

# 設定 OpenAI
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

@st.cache_resource
def get_embedding_model():
    return BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

@st.cache_resource(ttl=24 * 3600)
def configure_retriever():
    client = chromadb.PersistentClient(path=str(PathHelper.db_dir))
    collection = client.get_collection(name=CHROMA_DB)
    return collection

def get_relevant_documents(query: str, collection, model, top_k: int = 3) -> List[Dict]:
    query_embedding = model.encode(query, batch_size=1, max_length=8192)['dense_vecs']
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
        include=["documents", "metadatas"]
    )
    documents = [
        {"page_content": doc, "metadata": meta} 
        for doc, meta in zip(results['documents'][0], results['metadatas'][0])
    ]
    return documents

def generate_response(messages: List[Dict]) -> str:
    try:
        chat_completion = client.chat.completions.create(
            model=CHAT_MODEL_NAME,
            messages=messages,
            temperature=0,
            stream=True
        )
        full_response = ""
        for chunk in chat_completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                yield full_response
    except Exception as e:
        logger.error(f"OpenAI API 錯誤: {str(e)}")
        yield f"抱歉,發生了一個錯誤: {str(e)}"

def get_cumulative_query(messages: List[Dict]) -> str:
    return " ".join([msg["content"] for msg in messages if msg["role"] == "user"])

embedding_model = get_embedding_model()
collection = configure_retriever()

# 初始化或取得聊天歷史
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": INIT_MESSAGE}]

# 顯示聊天歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 使用者輸入
if user_query := st.chat_input(placeholder="請輸入您的問題"):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 取得累積的查詢
    cumulative_query = get_cumulative_query(st.session_state.messages)
    
    # 取得相關文件
    relevant_docs = get_relevant_documents(cumulative_query, collection, embedding_model, top_k=3)
    context = relevant_docs[0]['page_content'] if relevant_docs else ""

    # 準備傳送給 AI 的訊息
    messages_for_ai = [
        {"role": "system", "content": f"你是一位專業的健康、醫療和飲食相關的諮詢師。用繁體中文回覆。可以參考以下背景資訊但不限於此來回答問題:\n\n{context}\n除了以上資訊你可以再進行補充，回答不用過長，回答得有結構及完整就好。必要時可以跟使用者詢問更多資訊來提供給你。"},
    ] + st.session_state.messages[-5:]  # 只傳送最後5條訊息以節省 tokens

    # 產生回應
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        for response in generate_response(messages_for_ai):
            response_placeholder.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # 顯示相關影片的連結
    if relevant_docs:
        st.write("相關影片:")
        for i, doc in enumerate(relevant_docs, 1):
            video_id = doc['metadata']['video_id']
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            st.write(f"{i}. [{youtube_url}]({youtube_url})")

    # 在對話框外加入檢視相關影片的按鈕
    for i, doc in enumerate(relevant_docs, 1):
        video_id = doc['metadata']['video_id']
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        if st.button(f"檢視相關影片 {i}"):
            st.video(youtube_url)

# 側邊欄
st.sidebar.title("設定")
if st.sidebar.button("清除對話歷史"):
    st.session_state.messages = [{"role": "assistant", "content": INIT_MESSAGE}]
st.sidebar.info("這是一個基於 AI 的健康諮詢師")

if __name__ == "__main__":
    pass