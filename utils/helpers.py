from config.config import Config
from core.downloader import Downloader
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

@dataclass
class DownloadConfig:
    uri: str
    media_url: str
    output: Path = field(default=Path(Config.get("Constants")["DEFAULT_OUTPUT_PATH"]))
    name: str = ""

    def validate(self):
        if not self.uri and not self.media_url:
            raise ValueError("En az bir URL parametresi verilmelidir (uri veya media_url)")
        if self.uri and not self.uri.startswith("http"):
            raise ValueError("URI 'http' veya 'https' ile başlamalıdır")
        if self.media_url and not self.media_url.startswith("http"):
            raise ValueError("Media URL 'http' veya 'https' ile başlamalıdır")

# dosya adı verilmemişse bugünün tarih ve saatine göre otomatik isim oluştur
def resolve_output_name(output_name: str, index: int = None) -> str:
    if output_name:
        stem = Path(output_name).stem
        return f"{stem}_{index}.mp4" if index is not None else f"{stem}.mp4"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"video_{timestamp}_{index}.mp4" if index is not None else f"video_{timestamp}.mp4"

def multiple_download(media_urls: List[str], output_path, output_name=""):
    for i, url in enumerate(media_urls):
        print(f"\n--- [{i+1}/{len(media_urls)}] ---")
        name = resolve_output_name(output_name, index=i+1)
        downloader = Downloader(media_url=url, output_path=output_path, output_name=name)
        downloader.download()
