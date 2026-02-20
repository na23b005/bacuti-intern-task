import requests, time, os, urllib.parse

class NSEScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nseindia.com"
        })
        self.download_dir = "brsr_xmls"
        os.makedirs(self.download_dir, exist_ok=True)

    def initialize(self):
        self.session.get("https://www.nseindia.com")
        time.sleep(2)

    def get_company_list(self):
        url = "https://www.nseindia.com/api/corporate-bussiness-sustainabilitiy"
        return self.session.get(url).json().get("data", [])

    def download_xbrl(self, symbol, url):
        if not url or url == "-":
            return None

        filename = f"{symbol}_{url.split('/')[-1]}"
        path = os.path.join(self.download_dir, filename)

        quoted = urllib.parse.quote(f'"{url}"')
        api = f"https://www.nseindia.com/api/download_xbrl?fileUrl={quoted}"

        res = self.session.get(api)
        if res.status_code == 200:
            with open(path, 'wb') as f:
                f.write(res.content)
            time.sleep(1)
            return path
        return None
