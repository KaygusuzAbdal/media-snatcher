import requests
from pathlib import Path
from tqdm import tqdm
import utils.helpers as helper

"""
    Downloader sınıfı, verilen bir medya bağlantısını (örn. .mp4 veya .m3u8) belirtilen dosya yoluna indirir.
"""
class Downloader:
    def __init__(self, media_url:str, output_path:str, output_name:str = ""):

        # indirilecek medya dosyasının bağlantısı
        self.media_url = media_url
        
        # medyanın kaydedileceği dosya yolu
        # sonu / veya \ ile bitmese bile normalize edilir
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # içerik tipini belirle
        self.content_type = self._detect_content_type()

        # dosya adını oluştur (verilmişse kullan, yoksa otomatik üret)
        output_name = helper.resolve_output_name(output_name)

        # kaydedilecek dosya
        self.output_path = output_dir / output_name
        # klasör yoksa oluştur (örnek: 'downloads/' klasörü)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    # bağlantıya HEAD isteği göndererek içerik tipini kontrol eder
    def _detect_content_type(self) -> str:
        try:
            print(f"[+] Bağlantı kontrol ediliyor: {self.media_url}")
            response = requests.head(self.media_url, allow_redirects=True)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            print(f"[i] Content-Type: {content_type}")
            return content_type
        except Exception as e:
            print(f"[!] İçerik tipi alınırken hata oluştu: {e}")
            return ""

    # medya dosyasını belirtilen bağlantıdan indirir ve output_path'e kaydeder
    def download(self):
        try:
            # dosya tipi kontrolü (mp4 veya m3u8)
            if ".mp4" in self.media_url or "video/mp4" in self.content_type:
                print("[>] .mp4 dosyası bulundu. İndirme başlatılıyor...")
                self._download_mp4()
            elif ".m3u8" in self.media_url or "application/vnd.apple.mpegurl" in self.content_type:
                print("[>] .m3u8 dosyası bulundu. İndirme başlatılıyor...")
                self._download_m3u8()
            else:
                print("[!] Bilinmeyen içerik türü. İndirme işlemi iptal edildi.")

        except Exception as e:
            # Hata varsa yazdır
            print(f"[!] Hata oluştu: {e}")

    # .mp4 dosyalarını indirir
    def _download_mp4(self):
        try:
            print(f"[+] İndiriliyor: {self.media_url}")
            # Dosyayı stream modunda indiriyoruz (özellikle büyük dosyalar için gerekli)
            response = requests.get(self.media_url, stream=True)
            response.raise_for_status() # HTTP hatası varsa exception döndürür

            # dosya binary olarak yazılır, parça parça (chunk halinde) indirilir
            with open(self.output_path, 'wb') as f:
                for chunk in tqdm(response.iter_content(chunk_size=8192), desc="Downloading", unit='chunk'):
                    # Boş chunk'ları yazmaya gerek yok
                    if chunk:
                        f.write(chunk)

            print(f"[✓] İndirme tamamlandı: {self.output_path}")
            
        except Exception as e:
            # Hata varsa yazdır
            print(f"[!] Hata oluştu: {e}")
    
    # .m3u8 dosyalarını indirir
    def _download_m3u8(self):
        try:
            print(f"[+] m3u8 playlist indiriliyor: {self.media_url}")
            # m3u8 dosyasını indir
            response = requests.get(self.media_url)
            response.raise_for_status() # HTTP hatası varsa exception döndürür

            # dosya satırlarını ayırıyoruz
            lines = response.text.splitlines()
            # .ts segmentleri için temel URL'yi belirle (m3u8 dosyasının bulunduğu dizin)
            base_url = self.media_url.rsplit('/', 1)[0]

            # '#' ile başlamayan satırlar = .ts dosyası URL'leri
            ts_urls = [line for line in lines if line and not line.startswith("#")]
            if not ts_urls:
                print("[!] .ts segmenti bulunamadı.")
                return

            # .ts dosyalarını sırayla indir ve tek bir dosyada birleştir
            with open(self.output_path, 'wb') as f:
                for i, ts in enumerate(ts_urls):
                    ts_url = ts if ts.startswith("http") else f"{base_url}/{ts}"
                    print(f"[{i+1}/{len(ts_urls)}] Segment: {ts_url}")
                    ts_data = requests.get(ts_url).content
                    f.write(ts_data)

            print(f"[✓] m3u8 segmentleri birleştirildi ve .mp4 olarak kaydedildi: {self.output_path}")

        except Exception as e:
            # Hata varsa yazdır
            print(f"[!] m3u8 indirme sırasında hata oluştu: {e}")
