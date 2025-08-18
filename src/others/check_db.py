import chromadb
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import PathHelper

# 連接到現有的資料庫
client = chromadb.PersistentClient(path=str(PathHelper.db_dir))

# 刪除 collection
# client.delete_collection(name='Cofit211-test')

# 獲取現有的集合
collection = client.get_collection(name='Cofit211-cosine')

# 檢索所有文檔
# results = collection.get()

results= collection.get(
          include=['embeddings', 'documents', 'metadatas']
          )

# print(results['ids'])

# v = []
# for i in results['metadatas']:
#     v.append(i['video_id'])
# print(len(set(v)))

# 刪除資料
# collection.delete(ids=['', ''])



from FlagEmbedding import BGEM3FlagModel
model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
embeddings_list = []
text = '肚子痛該怎麼辦？'
embeddings = model.encode(text, 
                          batch_size=12, 
                          max_length=8192, 
                          )['dense_vecs']
embeddings_list.append(embeddings.tolist())

results_back = collection.query(
    query_embeddings=embeddings_list,
    # query_texts=text,
    n_results=3
)