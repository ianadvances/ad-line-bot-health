channel_name = 'Cofit211'

import json
import os
from pytubefix import YouTube
from pytubefix.cli import on_progress
from tqdm import tqdm
try:
    import sys
    from pathlib import Path
    
    # 將專案根目錄加入 Python 路徑以供匯入
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    import src.constants as const
    from src.utils import PathHelper, get_logger
except Exception as e:
    print(e)
    raise Exception("Please run this script from the root directory of the project")

logger = get_logger(__name__)

def download_audio(video_url, output_path):
    # 取得影片 ID
    video_id = video_url.split("=")[-1]
    output_file = f"{output_path}/{video_id}.mp3"

    # 如果檔案已存在，跳過下載
    if os.path.exists(output_file):
        logger.info(f"File already exists: {output_file}")
        return

    try:
        yt = YouTube(video_url, on_progress_callback = on_progress)
        print(yt.title)
         
        ys = yt.streams.get_audio_only()
        audio_file = ys.download(mp3=True, output_path=output_path, filename=f"{video_id}")
        
        logger.info(f"Audio successfully downloaded: {audio_file}")
    except Exception as e:
        logger.error(f"Error downloading audio for {video_url}: {str(e)}")

def main():
    entities = [i for i in os.listdir(PathHelper.entities_dir / f"{channel_name}") if i.endswith(".json")]
    m_docs = len(entities)
    m_docs_wo_transcript = 0
    m_docs_failed = 0

    for e in tqdm(entities, total=len(entities)):
        try:
            with open(PathHelper.entities_dir / f"{channel_name}" / e, "r") as f:
                data = json.load(f)
            
            # 下載音訊（如果沒有文字稿）
            if not data.get(const.TRANSCRIPT):
                m_docs_wo_transcript += 1
                download_audio(data[const.VIDEO_URL], PathHelper.audio_dir / f"{channel_name}")
        except Exception as e:
            logger.error(f"Error processing {e}: {str(e)}")
            m_docs_failed += 1
            continue

    logger.info(f"Total docs: {m_docs}")
    logger.info(f"Docs without transcript: {m_docs_wo_transcript}")
    logger.info(f"Docs failed: {m_docs_failed}")

if __name__ == "__main__":
    
    main()