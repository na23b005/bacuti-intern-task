from scraper import NSEScraper
from database import setup_database, insert_company_data
from parser import parse_xbrl_file
from queries import run_queries

def main():
    print("Step 1: Setting up database...")
    setup_database()

    print("Step 2: Initializing Scraper...")
    scraper = NSEScraper()
    scraper.initialize()
    
    companies = scraper.get_company_list()
    print(f"Found {len(companies)} companies. Processing...")

    # NOTE: For demonstration purposes, you might want to slice this list 
    # e.g., companies[:20] so you don't have to wait for 1000 files to download 
    # just to test if your code works.
    for i, comp in enumerate(companies):
        symbol = comp.get('symbol')
        xbrl_url = comp.get('xbrlFile')
        
        print(f"[{i+1}/{len(companies)}] Processing {symbol}...")
        
        filepath = scraper.download_xbrl(symbol, xbrl_url)
        
        if filepath:
            try:
                # Parse XML
                parsed_data = parse_xbrl_file(filepath, symbol)
                # Store in DB
                insert_company_data(parsed_data)
            except Exception as e:
                print(f"Error parsing/storing {symbol}: {e}")

    print("\nStep 3: Running Queries...")
    run_queries()
    
    print("\nProcess Complete!")

if __name__ == "__main__":
    main()