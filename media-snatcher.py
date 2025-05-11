from cli.args import get_args
from utils.helpers import DownloadConfig, multiple_download
from sniffer.generic import GenericSniffer
from core.downloader import Downloader
from config.config import Config


def main():
    args = get_args()

    # Config sınıfını yükle (config.json'dan)
    Config.load()

    # Download yapılandırmasını oluştur
    config = DownloadConfig(
        uri=args.url or "",
        media_url=args.media_url or "",
        output=args.output,
        name=args.name
    )

    try:
        config.validate()
    except ValueError as ve:
        print(f"[!] Geçersiz yapılandırma: {ve}")
        return

    if args.url:
        print("[~] işlem başlatılıyor...")
        sniffer = GenericSniffer(config.uri)
        found_links = sniffer.extract_links(method=args.method)

        if not found_links:
            print("[!] Hiçbir medya bağlantısı bulunamadı.")
            return

        print(f"[*] Toplam {len(found_links)} bağlantı bulundu.")
        multiple_download(found_links, config.output, config.name)

    # eğer sadece sniff istendiyse
    elif args.sniff:
        print("[~] Sniff işlemi başlatılıyor...")
        sniffer = GenericSniffer(config.uri)
        found_links = sniffer.extract_links(method=args.method)

        if not found_links:
            print("[!] Hiçbir medya bağlantısı bulunamadı.")
            return

        print(f"[*] Toplam {len(found_links)} bağlantı bulundu.")
        print(found_links)

    # eğer doğrudan medya URL'si verildiyse
    elif config.media_url:
        print("[~] Doğrudan medya bağlantısı indiriliyor...")
        downloader = Downloader(
            media_url=config.media_url,
            output_path=config.output,
            output_name=config.name
        )
        downloader.download()

    else:
        print("[!] Ne sniff işlemi ne de doğrudan medya bağlantısı belirtildi.")


if __name__ == "__main__":
    main()