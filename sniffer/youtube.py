import re
import json
import requests
from config.config import Config
from .base_sniffer import BaseSniffer

class YouTubeSniffer(BaseSniffer):
    def __init__(self, url: str):
        super().__init__(url)
        self.user_agent = Config.get("Constants")["USER_AGENT"]
        self.supported_extensions = Config.get("Constants")["SUPPORTED_EXTENSIONS"]

    def extract_links(self) -> list:
        print(f"[~] YouTube bağlantısı tespit edildi: {self.url}")
        try:
            response = requests.get(self.url, headers={"User-Agent": self.user_agent})
            response.raise_for_status()
            html = response.text

            match = re.search(r'ytInitialPlayerResponse\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
            if not match:
                print("[!] ytInitialPlayerResponse bulunamadı.")
                return []

            data = json.loads(match.group(1))
            formats = data.get("streamingData", {}).get("adaptiveFormats", [])

            urls = []
            for f in formats:
                if 'url' in f and any(ext in f.get("mimeType", "") for ext in self.supported_extensions):
                    urls.append(f['url'])
                elif 'signatureCipher' in f:
                    print("[!] Bu format şifreli. Şu an çözüm desteği yok.")

            if urls:
                print(f"[✓] {len(urls)} çözülmemiş medya bağlantısı bulundu (YouTube)")
            else:
                print("[!] Çözülebilir doğrudan medya bağlantısı bulunamadı.")

            return urls

        except Exception as e:
            print(f"[!] YouTube sniff sırasında hata oluştu: {e}")
            return []
