from pathlib import Path

class PathHelper:
    base_dir = Path(__file__).resolve().parent.parent.parent
    root_dir = base_dir
    data_dir = base_dir / "data"
    entities_dir = data_dir / "entities"
    text_dir = data_dir / "text"
    audio_dir = data_dir / "audio"
    db_dir = data_dir / "db"

    @staticmethod
    def ensure_dirs():
        PathHelper.data_dir.mkdir(parents=True, exist_ok=True)
        PathHelper.entities_dir.mkdir(parents=True, exist_ok=True)
        PathHelper.text_dir.mkdir(parents=True, exist_ok=True)
        PathHelper.audio_dir.mkdir(parents=True, exist_ok=True)
        PathHelper.db_dir.mkdir(parents=True, exist_ok=True)
