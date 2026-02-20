from scraper import NSEScraper
from database import setup_database, insert_company_data
from parser import parse_xbrl_file
from queries import run_queries

def main():
    setup_database()

    scraper = NSEScraper()
    scraper.initialize()

    companies = scraper.get_company_list()

    for comp in companies:
        symbol = comp['symbol']
        filepath = scraper.download_xbrl(symbol, comp['xbrlFile'])

        if filepath:
            data = parse_xbrl_file(filepath, symbol)
            insert_company_data(data)

    run_queries()

if __name__ == "__main__":
    main()
