from bs4 import BeautifulSoup
import re


def extract_value(soup, local_tag_name, context_ref="DCYMain"):
    """
    Finds a tag by its local name (ignoring namespace prefix) and contextRef.
    XBRL tags look like: <in-capmkt:TotalScope1Emissions contextRef="DCYMain" ...>
    BeautifulSoup with lxml-xml parser keeps the full namespaced name, so we
    search by regex on the tag name.
    """
    # Match any namespace prefix, e.g. "in-capmkt:TotalScope1Emissions"
    # Added start anchor ^ to avoid partial matches
    pattern = re.compile(r'^(?:[\w-]+:)?' + re.escape(local_tag_name) + r'$', re.IGNORECASE)
    tags = soup.find_all(pattern)
    for tag in tags:
        ctx = tag.get('contextref') or tag.get('contextRef', '')
        if re.search(context_ref, ctx, re.IGNORECASE):
            text = tag.text.strip()
            if text and text.lower() not in ('na', 'n/a', ''):
                try:
                    return float(text)
                except ValueError:
                    continue
    return 0.0


def extract_text(soup, local_tag_name, context_ref=None):
    """Extracts a text value from a tag, optionally filtering by contextRef."""
    try:
        # Added start anchor ^ to avoid partial matches
        pattern = re.compile(r'^(?:[\w-]+:)?' + re.escape(local_tag_name) + r'$', re.IGNORECASE)
        tags = soup.find_all(pattern)
        for tag in tags:
            if context_ref:
                ctx = tag.get('contextref') or tag.get('contextRef', '')
                if not re.search(context_ref, ctx, re.IGNORECASE):
                    continue
            text = tag.text.strip()
            if text and text.lower() not in ('na', 'n/a', ''):
                return text
        return None
    except AttributeError:
        return None


def parse_xbrl_file(filepath, symbol):
    """
    Parses an XBRL/XML file and returns a dictionary of extracted fields.

    Key fixes vs original parser:
    1. Tags are namespaced (in-capmkt:TagName) - we match by local name only.
    2. NameOfTheCompany uses contextRef="ICYMain", not "DCYMain".
    3. TotalElectricityConsumption is NOT a direct tag. It must be computed as:
         TotalElectricityConsumptionFromRenewableSources
       + TotalElectricityConsumptionFromNonRenewableSources
    """
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'lxml-xml')

    data = {'symbol': symbol}

    # NameOfTheCompany uses ICYMain context (not DCYMain)
    name = (
        extract_text(soup, 'NameOfTheCompany', context_ref='ICYMain')
        or extract_text(soup, 'NameOfTheCompany')  # fallback: any context
        or symbol
    )
    data['NameOfTheCompany'] = name

    # WebsiteOfCompany
    website = (
        extract_text(soup, 'WebsiteOfCompany', context_ref='DCYMain')
        or extract_text(soup, 'WebsiteOfCompany')
        or 'N/A'
    )
    data['WebsiteOfCompany'] = website

    # Emissions - all DCYMain
    data['TotalScope1Emissions'] = extract_value(soup, 'TotalScope1Emissions', 'DCYMain')
    data['TotalScope2Emissions'] = extract_value(soup, 'TotalScope2Emissions', 'DCYMain')
    data['TotalScope3Emissions'] = extract_value(soup, 'TotalScope3Emissions', 'DCYMain')

    # Turnover
    data['Turnover'] = extract_value(soup, 'Turnover', 'DCYMain')

    # Electricity: renewable + non-renewable (there is no combined tag in the XML)
    renewable = extract_value(soup, 'TotalElectricityConsumptionFromRenewableSources', 'DCYMain')
    non_renewable = extract_value(soup, 'TotalElectricityConsumptionFromNonRenewableSources', 'DCYMain')
    total_electricity = renewable + non_renewable

    data['TotalElectricityConsumptionFromRenewableSources'] = renewable
    data['TotalElectricityConsumptionFromNonRenewableSources'] = non_renewable
    data['TotalElectricityConsumption'] = total_electricity  # computed field

    return data