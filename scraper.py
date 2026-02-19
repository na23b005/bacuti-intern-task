import requests
import time
import os
import urllib.parse

class NSEScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-bussiness-sustainabilitiy-reports",
            "X-Requested-With": "XMLHttpRequest"
        })
        self.download_dir = "brsr_xmls"
        os.makedirs(self.download_dir, exist_ok=True)

    def initialize(self):
        self.session.get("https://www.nseindia.com", timeout=10)
        time.sleep(2)

    def get_company_list(self):
        url = "https://www.nseindia.com/api/corporate-bussiness-sustainabilitiy"
        res = self.session.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    def download_xbrl(self, symbol, xbrl_url):
        if not xbrl_url or xbrl_url == "-":
            return None
            
        filename = f"{symbol}_{xbrl_url.split('/')[-1]}"
        filepath = os.path.join(self.download_dir, filename)
        
        if os.path.exists(filepath):
            return filepath
            
        # Wrap the URL in quotes as expected by the server
        quoted_url = f'"{xbrl_url}"'
        encoded_url = urllib.parse.quote(quoted_url)
        api_url = f"https://www.nseindia.com/api/download_xbrl?fileUrl={encoded_url}"
        
        try:
            res = self.session.get(api_url, timeout=15)
            if res.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(res.content)
                time.sleep(1) # Rate limiting
                return filepath
        except Exception as e:
            pass
            # print(f"Failed to download {symbol}: {e}")
        return None