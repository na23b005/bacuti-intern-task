from database import get_connection
from tabulate import tabulate

def run_queries():
    conn = get_connection()
    cursor = conn.cursor()

    print("\n--- QUERY A: Top 10 Lowest Emissions Intensity ---")
    # Error Handling Example (Discussion Q6): Using "WHERE turnover > 0" 
    # prevents a Division By Zero SQL error if a company reported 0 turnover.
    cursor.execute('''
        SELECT company_name, 
               ROUND((scope1_emissions + scope2_emissions) / turnover, 6) AS emissions_intensity 
        FROM company_emissions 
        WHERE turnover > 0 AND (scope1_emissions + scope2_emissions) > 0
        ORDER BY emissions_intensity ASC 
        LIMIT 10
    ''')
    results_a = cursor.fetchall()
    print(tabulate(results_a, headers=["Company Name", "Emissions Intensity"], tablefmt="grid"))

    print("\n--- QUERY B: Top 10 Highest Renewable Energy Usage ---")
    cursor.execute('''
        SELECT company_name, 
               ROUND((renewable_electricity / total_electricity) * 100, 2) AS renewable_percentage 
        FROM company_emissions 
        WHERE total_electricity > 0 
        ORDER BY renewable_percentage DESC 
        LIMIT 10
    ''')
    results_b = cursor.fetchall()
    print(tabulate(results_b, headers=["Company Name", "% Renewable Energy"], tablefmt="grid"))

    conn.close()