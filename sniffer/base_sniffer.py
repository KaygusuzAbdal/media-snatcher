import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from playwright.sync_api import sync_playwright
from config.config import Config
from abc import ABC, abstractmethod

# BaseSniffer sınıfı, verilen bir URL'deki HTML ve network trafiğinden .mp4 veya .m3u8 uzantılı medya bağlantılarını yakalamaya çalışır
class BaseSniffer(ABC):
    def __init__(self, url: str):
        self.url = url
        self.supported_extensions = Config.get("Constants")["SUPPORTED_EXTENSIONS"]
        self.user_agent = Config.get("Constants")["USER_AGENT"]

    # Medya bağlantılarını çıkarır
    # methods: 'auto', 'playwright', 'selenium', 'static'
    # 'auto' ise önce playwright denenir, başarısızsa selenium çalıştırılır
    @abstractmethod
    def extract_links(self, method: str = "auto") -> list:
        pass

    # sayfanın HTML içeriğini indirip .mp4 ve .m3u8 bağlantılarını regex ile arar
    def _sniff_static(self) -> list:
        print("[i] Sayfa içeriği analiz ediliyor (static mode)")
        try:
            response = requests.get(self.url, headers={"User-Agent": self.user_agent})
            response.raise_for_status()
            content = response.text

            # regex ile medya bağlantılarını bul
            pattern = r'(https?://[^\s"\']+\.(' + '|'.join(self.supported_extensions) + '))'
            matches = re.findall(pattern, content, re.IGNORECASE)
            urls = list(set(match[0] for match in matches))

            print(f"[✓] {len(urls)} medya bağlantısı bulundu (static)") if urls else print("[!] Hiçbir medya bağlantısı bulunamadı (static)")
            return urls
        except Exception as e:
            print(f"[!] Static analiz sırasında hata oluştu: {e}")
            return []

    # request geldiğinde çalışacak fonksiyon (helper for playwright)
    def _extract_from_response(self, response, media_urls):
        try:
            url = response.url
            # eğer request içerisinde medya bağlantıları varsa
            if any(ext in url.lower() for ext in self.supported_extensions):
                media_urls.append(url)
        except:
            pass

    # playwright kullanarak gerçek tarayıcı ile network trafiği dinlenir
    def _sniff_playwright(self) -> list:
        print("[i] Playwright ile network dinleniyor...")
        media_urls = []
        try:
            with sync_playwright() as p:
                # tarayıcıyı aç
                browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                context = browser.new_context()
                page = context.new_page()

                # her request geldiğinde _extract_from_response fonksiyonu ile kontrol et
                page.on("response", lambda response: self._extract_from_response(response, media_urls))
                # tüm network bağlantıları durana kadar bekle
                page.goto(self.url, wait_until="networkidle")
                # network bağlantıları bittiğinde tarayıcıyı kapat
                browser.close()

            media_urls = list(set(media_urls))
            print(f"[✓] {len(media_urls)} medya bağlantısı bulundu (playwright)") if media_urls else print("[!] Hiçbir medya bağlantısı bulunamadı (playwright)")
            return media_urls
        except Exception as e:
            print(f"[!] Playwright kullanılırken hata oluştu: {e}")
            return []

    # selenium ile Chrome tarayıcıyı başlatıp, performans logları üzerinden medya linklerini çeker.
    def _sniff_selenium(self) -> list:
        print("[i] Selenium ile network logları taranıyor...")
        media_urls = set()
        try:
            # headless modda çalışan bir Chrome başlat
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            # performans loglarını aktifleştir (network trafiğini görebilmek için)
            options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

            driver = webdriver.Chrome(options=options)
            driver.get(self.url) # belirtilen URL'ye git

            # tarayıcının network loglarını al
            logs = driver.get_log("performance")
            pattern = r'https?://[^\s"\']+\.(' + '|'.join(self.supported_extensions) + ')'
            for entry in logs:
                message = entry['message']
                matches = re.findall(pattern, message, re.IGNORECASE)
                for match in matches:
                    full_match = re.search(r'https?://[^\s"\']+\.' + match, message, re.IGNORECASE)
                    if full_match:
                        media_urls.add(full_match.group(0))

            driver.quit() # tarayıcıyı kapat
            media_urls = list(media_urls)
            print(f"[✓] {len(media_urls)} medya bağlantısı bulundu (selenium)") if media_urls else print("[!] Hiçbir medya bağlantısı bulunamadı (selenium)")
            return media_urls
        except Exception as e:
            print(f"[!] Selenium kullanılırken hata oluştu: {e}")
            return []
