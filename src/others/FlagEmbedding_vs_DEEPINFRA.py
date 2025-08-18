import os
from FlagEmbedding import BGEM3FlagModel
from openai import OpenAI
import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import PathHelper

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

openai = OpenAI(
    api_key='',
    base_url="https://api.deepinfra.com/v1/openai",
)

files = os.listdir(PathHelper.text_dir / 'test')

if '.DS_Store' in files:
    del(files[0])

for file in files:
    with open(PathHelper.text_dir / 'test' / file, encoding="utf8") as f:
        transcript = f.readlines()
        text = eval(transcript[0])
    # text = text[:800]
    
    embeddings_1 = model.encode(text, 
                                batch_size=12, 
                                max_length=8192, 
                                )['dense_vecs']
    
    
    embeddings = openai.embeddings.create(
        model="BAAI/bge-m3",
        input=text,
        encoding_format="float"
    )
    
    # print('================================')
    print(f"text length: {len(text)}")
    print(f"Tokens used for embedding: {embeddings.usage.prompt_tokens}")
    # print(f'{len(text)} / {embeddings.usage.prompt_tokens} = {round(len(text)/embeddings.usage.prompt_tokens, 2)}')
    
    embeddings_2 = embeddings.data[0].embedding
    embeddings_2 = np.array(embeddings_2)
    
    
    plt.plot(embeddings_1)
    plt.plot(embeddings_2)
    plt.show()