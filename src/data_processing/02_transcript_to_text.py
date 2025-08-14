channel_name = 'Cofit211'

import json
import os

from deepmultilingualpunctuation import PunctuationModel
from dotenv import load_dotenv

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

# 載入環境變數
dotenv_path = PathHelper.root_dir / ".env"
load_dotenv(dotenv_path=dotenv_path)

# 日誌記錄器
logger = get_logger(__name__)

# 初始化模型
logger.info("init punctuation model")
punct_model = PunctuationModel()

# 處理函數
def preprocess_transcript(transcript):
    """
    為轉錄文字加入標點符號並合併為一個文件
    """
    # 分割為長度為 n 的清單
    n = 5
    transcript_text = [transcript[i : i + n] for i in range(0, len(transcript), n)]

    # 恢復標點符號
    transcript_text_restore = []
    for transcript_text_i in transcript_text:
        result_punct = punct_model.restore_punctuation(" ".join(transcript_text_i))
        transcript_text_restore.append(result_punct)

    # 合併轉錄文字
    transcript = "\n".join(transcript_text_restore)

    return transcript


def main():
    # 選擇檔案
    entities = [i for i in os.listdir(PathHelper.entities_dir / f"{channel_name}") if i.endswith(".json")]

    logger.info(f"# files: {len(entities)}")

    # 文字轉文字
    m_transcripts_processed = 0
    for jf in entities:
        fname = jf.split(".")[0]
        try:
            with open((PathHelper.entities_dir / f"{channel_name}" / jf), "r") as f:
                ent_i = json.load(f)

            # 如果檔案存在，則跳過
            if (PathHelper.text_dir / f"{channel_name}" / f"{fname}.txt").exists():
                logger.info(f"file exist: {fname}")
                continue

            # 如果實體中有轉錄文字，則儲存文字
            if ent_i.get("transcript"):
                transcript_text = [t["text"] for t in ent_i["transcript"]]

                # 預處理轉錄文字
                transcript = preprocess_transcript(transcript_text)

                # 以編碼儲存轉錄文字
                with open(
                    PathHelper.text_dir / f"{channel_name}" / f"{fname}.txt", "w", encoding="utf8"
                ) as f:
                    json.dump(transcript, f)

                m_transcripts_processed += 1
            
            else:
                logger.info(f"file no transcript: {fname}")

        except Exception as e:
            logger.error(e)
            continue

    # 日誌記錄
    logger.info(f"extract transcript from {m_transcripts_processed} files")


if __name__ == "__main__":

    main()