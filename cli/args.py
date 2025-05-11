import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Medya İndirme Aracı (mp4/m3u8)")

    parser.add_argument(
        "-u", "--url",
        required=True,
        help="medyanın indirileceği URL (sniff yapılacak sayfa URL'si)"
    )

    parser.add_argument(
        "-o", "--output",
        default="downloads",
        help="dosyaların kaydedileceği klasör (varsayılan: downloads/)"
    )

    parser.add_argument(
        "-n", "--name",
        default="",
        help="indirilecek dosya için opsiyonel isim (örn: video.mp4)"
    )

    parser.add_argument(
        "-s", "--sniff",
        action="store_true",
        help="verilen sayfada sniff işlemi yaparak medya bağlantılarını yakala"
    )

    parser.add_argument(
        "-m", "--method",
        default="auto",
        choices=["auto", "static", "playwright", "selenium"],
        help="sniff yöntemi: static, playwright, selenium veya auto (önce static dener)"
    )

    parser.add_argument(
        "-mu", "--media-url",
        help="medyanın doğrudan URL'si (sniff işlemi yapmadan indirme)"
    )

    return parser.parse_args()
