channel_name = 'Cofit211'

import json
import os

from deepmultilingualpunctuation import PunctuationModel
from dotenv import load_dotenv
from faster_whisper import WhisperModel
# from pydub import AudioSegment
from tqdm import tqdm

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


def chunk_text(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def restore_punctuation_in_chunks(punct_model, text, chunk_size):
    chunks = chunk_text(text, chunk_size)
    results = []
    for chunk in chunks:
        result = punct_model.restore_punctuation(chunk)
        results.append(result)
    return " ".join(results)


def main():

    logger.info(f"channel_name: {channel_name}")

    # 初始化模型
    punct_model = PunctuationModel()

    # 選擇檔案
    fnames = [i for i in os.listdir(PathHelper.audio_dir / f"{channel_name}") if i.endswith(".mp3")]
    fnames_has_text = [i for i in os.listdir(PathHelper.text_dir / f"{channel_name}") if i.endswith(".txt")]
    fnames_wo_text = list(set(fnames) - set(fnames_has_text))
    logger.info(f"# files has text (all): {len(fnames_has_text)}")
    logger.info(f"# files without text (all): {len(fnames_wo_text)}")

    # 選擇檔案子集
    json_files = os.listdir(PathHelper.entities_dir / f"{channel_name}")
    entities_selected = []
    for jf in json_files:
        fname = jf.split(".")[0]
        try:
            with open(PathHelper.entities_dir / f"{channel_name}" / jf, "r") as f:
                ent_i = json.load(f)

            # # if having transcript from entities, then save text
            # if ent_i.get("transcript"):
            #     transcript_text = [t["text"] for t in ent_i["transcript"]]

            #     # split into list of list with length 50
            #     transcript_text = [
            #         transcript_text[i : i + 50]
            #         for i in range(0, len(transcript_text), 50)
            #     ]

            #     # restore punctuation
            #     transcript_text_restore = []
            #     for transcript_text_i in transcript_text:
            #         result_punct = punct_model.restore_punctuation(
            #             " ".join(transcript_text_i)
            #         )
            #         transcript_text_restore.append(result_punct)

            #     # merge transcripts
            #     transcript = "\n".join(transcript_text_restore)

            #     # save transcript with encoding
            #     with open(
            #         PathHelper.text_dir / f"{channel_name}" / f"{fname}.txt", "w", encoding="utf8"
            #     ) as f:
            #         json.dump(transcript, f)

            # 如果是選定的頻道，則加入到 entities_selected
            if channel_name:
                if ent_i.get("channel_name") == channel_name:
                    entities_selected.append(f"{ent_i['video_id']}.mp3")
            else:
                entities_selected.append(f"{ent_i['video_id']}.mp3")

        except Exception as e:
            logger.error(e)
            continue

    # 日誌記錄
    fnames_selected = set(fnames_wo_text).intersection(set(entities_selected))
    logger.info(f"# files w/o text: {len(fnames_selected)}")

    limit = 0
    if limit > 0:
        logger.info("limiting the size of the subset of files to be processed")
        fnames_selected = list(fnames_selected)[: limit]

    logger.info(f"# files selected: {len(fnames_selected)}")

    # 音訊轉文字
    # 使用 faster whisper
    model_size = "large-v3"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    # total_sec = 0
    for fname_ext in tqdm(fnames_selected):
        fname = fname_ext.split(".")[0]
        if (PathHelper.text_dir / f"{channel_name}" / f"{fname}.txt").exists():
            logger.info(f"file exist: {fname}")
            continue
        # audio_file = AudioSegment.from_mp3(PathHelper.audio_dir / f"{channel_name}" / fname_ext)
        # logger.info(f"fname: {fname}")

        # 取得總秒數
        # total_sec += audio_file.duration_seconds

        # 估計成本
        # estimated_cost = total_sec / 60 * 0.006 * 32
        # logger.info("estimated cost in TWD: ${:.2f}".format(estimated_cost))

        # 音訊轉文字並合併
        seg_i = []
        segments, info = model.transcribe(
            str(PathHelper.audio_dir / f"{channel_name}" / fname_ext),
            beam_size=5,
            initial_prompt="以下是普通話的句子。",
        )
        logger.info(
            "Detected language '%s' with probability %f"
            % (info.language, info.language_probability)
        )

        if info.language not in ("en", "zh"):
            with open(PathHelper.text_dir / f"{channel_name}" / f"{fname}.txt", "w") as f:
                json.dump("", f)
            continue

        for segment in segments:
            # print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            seg_i.append([segment.start, segment.end, segment.text])

        # 合併轉錄文字
        transcript_text = [
            [s[2] for s in seg_i[i: i + 10]] for i in range(0, len(seg_i), 10)
        ]
        transcript_text_restore = []
        for transcript_text_i in transcript_text:
            result_punct = restore_punctuation_in_chunks(punct_model, " ".join(transcript_text_i), 512)
            transcript_text_restore.append(result_punct)

        transcript_processed = "".join(transcript_text_restore)

        # 儲存轉錄文字
        with open(PathHelper.text_dir / f"{channel_name}" / f"{fname}.txt", "w") as f:
            json.dump(transcript_processed, f)


if __name__ == "__main__":

    main()
