import json
import sys
from pathlib import Path

# 將專案根目錄加入 Python 路徑以供匯入
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import PathHelper

with open(PathHelper.text_dir / 'Cofit211' / 'Dwt2VAqdrlg.txt', "r", encoding="utf8") as f:
    transcript = json.load(f)
    

#%%    
# from opencc import OpenCC

# def convert_simplified_to_traditional(text):
#     # 初始化 OpenCC，設定為簡體到繁體的轉換
#     cc = OpenCC('s2t')
#     # 轉換簡體中文到繁體中文
#     traditional_text = cc.convert(text)
#     return traditional_text

# # 測試範例
# simplified_text = transcript
# traditional_text = convert_simplified_to_traditional(simplified_text)

# with open('/Users/ianchen/Documents/line-bot-health/text/Cofit211/u-IQP_jpewU-.txt', "w") as f:
#     json.dump(traditional_text[400:], f)