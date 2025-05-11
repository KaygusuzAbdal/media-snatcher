from .base_sniffer import BaseSniffer

class GenericSniffer(BaseSniffer):
    def extract_links(self, method: str = "auto") -> list:
        print(f"[+] Medya bağlantıları aranıyor: {self.url} | Yöntem: {method}")

        if any(platform in self.url for platform in ["youtube.com", "twitter.com", "instagram.com"]):
            print("[!] Bu platform için özel bir sniffer kullanılmalıdır.")
            return []

        if method == "static":
            return self._sniff_static()
        elif method == "playwright":
            return self._sniff_playwright()
        elif method == "selenium":
            return self._sniff_selenium()
        elif method == "auto":
            # Önce static denenir, sonuç yoksa playwright, onda da sonuç yoksa selenium denenir
            for sniff_method in [self._sniff_static, self._sniff_playwright, self._sniff_selenium]:
                results = sniff_method()
                if results:
                    return results
            return []
        else:
            print(f"[!] Tanımsız yöntem: {method}")
            return []