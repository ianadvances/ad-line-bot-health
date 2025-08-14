channel_name = 'Cofit211'

import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from youtube_transcript_api import YouTubeTranscriptApi

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

# 日誌記錄器
logger = get_logger(__name__)

def main():
    logger.info(f"channel_name: {channel_name}")

    # 初始化驅動程式
    driver = webdriver.Chrome()

    url = f"https://www.youtube.com/@{channel_name}"
    driver.get(url + "/videos")

    # 捲動頁面
    ht = driver.execute_script("return document.documentElement.scrollHeight;")
    while True:
        prev_ht = driver.execute_script("return document.documentElement.scrollHeight;")
        driver.execute_script(
            "window.scrollTo(0, document.documentElement.scrollHeight);"
        )
        time.sleep(2)
        ht = driver.execute_script("return document.documentElement.scrollHeight;")
        if prev_ht == ht:
            break

    # 儲存
    # https://stackoverflow.com/questions/74578175/getting-video-links-from-youtube-channel-in-python-selenium
    videos = []
    try:
        for e in WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#details"))
        ):
            # 屬性
            title = e.find_element(By.CSS_SELECTOR, "a#video-title-link").get_attribute(
                "title"
            )
            vurl = e.find_element(By.CSS_SELECTOR, "a#video-title-link").get_attribute(
                "href"
            )

            # 加入
            videos.append(
                {
                    const.VIDEO_URL: vurl,
                    const.TITLE: title,
                }
            )
    except Exception as e:
        e
        pass

    logger.info(f"# videos from {channel_name}: {len(videos)}")

    # 取得轉錄文字
    for video_i in videos:
        video_id = video_i[const.VIDEO_URL].split("=")[-1]
        video_i[const.VIDEO_ID] = video_id
        video_i[const.CHANNEL_NAME] = channel_name
        logger.info(f"video id: {video_id}")

        entity_fname = PathHelper.entities_dir / f"{channel_name}/{video_i[const.VIDEO_ID]}.json"

        # 檢查檔案是否存在
        if entity_fname.exists():
            logger.info(f"file exist: {entity_fname}")
            # 跳到下一個影片
            continue

        try:
            transcript_i = YouTubeTranscriptApi.get_transcript(
                video_id, languages=["zh-TW"]
            )
            video_i[const.TRANSCRIPT] = transcript_i
        except Exception as e:
            e
            video_i[const.TRANSCRIPT] = []
        finally:
            # 將物件儲存為 json 到本地
            with open(
                PathHelper.entities_dir / f"{channel_name}/{video_i[const.VIDEO_ID]}.json", "w"
            ) as f:
                json.dump(video_i, f)


if __name__ == "__main__":

    main()
