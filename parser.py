import re
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

ENERGY_FACTORS = {
    # Nano
    'nanojoule': 1e-18,

    # Micro
    'microjoule': 1e-15,

    # Milli
    'millijoule': 1e-12,

    # Joule
    'joule': 1e-9,

    # Kilo
    'kilojoule': 1e-6,

    # Mega
    'megajoule': 1e-3,

    # Giga (base)
    'gigajoule': 1.0,

    # Tera
    'terajoule': 1e3,

    # Peta
    'petajoule': 1e6,

    # Exa
    'exajoule': 1e9,
}


EMISSION_FACTORS = {
    # Nano
    'nanotco2e': 1e-12,

    # Micro
    'microtco2e': 1e-9,

    # Milli
    'millitco2e': 1e-6,

    # Kilogram CO2e
    'kilogramco2e': 1e-6,

    # Tonne CO2e
    'tco2e': 1e-3,
    'tonne': 1e-3,
    'tonnes': 1e-3,

    # Kilotonne (base)
    'ktco2e': 1.0,

    # Megatonne
    'mtco2e': 1e3,

    # Gigatonne
    'gtco2e': 1e6,
}


CURRENCY_FACTORS = {
    'inr': 1.0, 'rs': 1.0,
    'usd': 83.0, 'eur': 90.0, 'gbp': 105.0,
}

def safe_float(text):
    try:
        return float(text.replace(',', '').strip())
    except:
        return None

def normalize_value(value, unit):
    if value is None or not unit:
        return value

    u = unit.lower()

    all_factors = {}
    all_factors.update(ENERGY_FACTORS)
    all_factors.update(EMISSION_FACTORS)
    all_factors.update(CURRENCY_FACTORS)

    for key in sorted(all_factors.keys(), key=len, reverse=True):
        if key in u:
            return value * all_factors[key]

    logging.warning(f"Unknown unit: {unit}")
    return value

def find_tags(soup, name):
    pattern = re.compile(r'^(?:[\w-]+:)?' + re.escape(name) + r'$', re.IGNORECASE)
    return soup.find_all(pattern)

def extract_value(soup, tag_name, context="DCYMain"):
    for tag in find_tags(soup, tag_name):
        ctx = tag.get('contextref') or tag.get('contextRef', '')
        if context.lower() not in ctx.lower():
            continue

        val = safe_float(tag.text.strip())
        if val is None:
            continue

        unit = tag.get('unitRef') or tag.get('unitref') or ''
        return normalize_value(val, unit)

    return 0.0

def extract_text(soup, tag_name, context=None):
    for tag in find_tags(soup, tag_name):
        if context:
            ctx = tag.get('contextref') or tag.get('contextRef', '')
            if context.lower() not in ctx.lower():
                continue
        return tag.text.strip()
    return None

def parse_xbrl_file(filepath, symbol):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        soup = BeautifulSoup(f.read(), 'lxml-xml')

    data = {'symbol': symbol}

    data['NameOfTheCompany'] = extract_text(soup, 'NameOfTheCompany') or symbol
    data['WebsiteOfCompany'] = extract_text(soup, 'WebsiteOfCompany') or 'N/A'

    data['TotalScope1Emissions'] = extract_value(soup, 'TotalScope1Emissions')
    data['TotalScope2Emissions'] = extract_value(soup, 'TotalScope2Emissions')
    data['TotalScope3Emissions'] = extract_value(soup, 'TotalScope3Emissions')

    data['Turnover'] = extract_value(soup, 'Turnover')

    renewable = extract_value(soup, 'TotalElectricityConsumptionFromRenewableSources')
    non_renewable = extract_value(soup, 'TotalElectricityConsumptionFromNonRenewableSources')

    data['TotalElectricityConsumptionFromRenewableSources'] = renewable
    data['TotalElectricityConsumptionFromNonRenewableSources'] = non_renewable
    data['TotalElectricityConsumption'] = renewable + non_renewable

    return data
