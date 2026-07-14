from __future__ import annotations

from hashlib import md5
from pathlib import Path
import urllib.request

import yaml


class DatasetRegistry:
    def __init__(self, path: Path):
        self.path = path
        self.data = yaml.safe_load(path.read_text())["datasets"]

    def get(self, name: str) -> dict:
        if name not in self.data:
            raise KeyError(f"unknown dataset: {name}")
        return self.data[name]

    def list(self):
        return self.data

    def download(self, name: str, out_dir: Path) -> Path:
        item = self.get(name)
        source = item.get("source") or {}
        url = item.get("download_url") or source.get("download_url")
        if not url:
            raise RuntimeError("dataset requires manual acceptance or an external downloader")
        if not str(url).startswith(("http://", "https://")):
            raise RuntimeError(f"dataset download is not directly fetchable: {url}")
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / Path(url).name
        urllib.request.urlretrieve(url, target)
        return target

    @staticmethod
    def md5sum(path: Path) -> str:
        h = md5()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
