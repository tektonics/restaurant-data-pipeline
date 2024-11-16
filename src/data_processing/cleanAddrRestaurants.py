import pandas as pd
import re
from ..config.config import RAW_RESTAURANTS_CSV, CLEANED_RESTAURANTS_CSV
from ..config.config import state_abbreviations

def clean_and_split_address(address):
    if not address:
        return {"Address": "", "City": "", "State": "", "Zip": ""}

    for full_state, abbrev in state_abbreviations.items():
        address = re.sub(r'\b' + re.escape(full_state) + r'\b', abbrev, address, flags=re.IGNORECASE)

    address = re.sub(r'\s+,', ',', address)
    address = re.sub(r',\s+', ', ', address)

    parts = [part.strip() for part in address.split(',') if part.strip()]
    cleaned_address_components = {"Address": "", "City": "", "State": "", "Zip": ""}

    dc_zip_match = re.match(r'^D\.C\.\s*(\d{5}(?:-\d{4})?)$', parts[-1])
    if dc_zip_match:
        cleaned_address_components["City"] = "WA"
        cleaned_address_components["State"] = "DC"
        cleaned_address_components["Zip"] = dc_zip_match.group(1)
        parts.pop()
    else:
        if parts:
            last_part = parts[-1]
            state_zip_match = re.match(r'^([A-Z]{2})\s*(\d{5}(?:-\d{4})?)$', last_part)
            
            if state_zip_match:
                cleaned_address_components["State"] = state_zip_match.group(1)
                cleaned_address_components["Zip"] = state_zip_match.group(2)
                parts.pop()
            else:
                zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', last_part)
                if zip_match:
                    cleaned_address_components["Zip"] = zip_match.group(1)
                    state_part = last_part.replace(zip_match.group(1), '').strip()
                    if len(state_part) == 2 and state_part.isupper():
                        cleaned_address_components["State"] = state_part
                    parts.pop()
                elif len(last_part) == 2 and last_part.isupper():
                    cleaned_address_components["State"] = last_part
                    parts.pop()

    if len(parts) > 1:
        cleaned_address_components["City"] = parts.pop()

    if cleaned_address_components["State"] == "DC" and not cleaned_address_components["City"]:
        cleaned_address_components["City"] = "WA"

    cleaned_address_components["Address"] = ', '.join(parts)

    address = cleaned_address_components["Address"]
    address = re.sub(r'(\d+)\s*&\s*(\d+[A-Za-z]?)', r'\1-\2', address)
    address = re.sub(r'\b(floor|fl|ste|suite|#)\s*(\d+)', r'#\2', address, flags=re.IGNORECASE)
    cleaned_address_components["Address"] = address

    return cleaned_address_components

def fill_missing_city(df):
    grouped = df.groupby(['State', 'Zip'])
    for (state, zip_code), group in grouped:
        cities = group['City'][group['City'] != ''].unique()
        if len(cities) == 1:
            df.loc[(df['State'] == state) & (df['Zip'] == zip_code), 'City'] = cities[0]
    return df

def remove_duplicates(df):
    df = df.sort_values(['Restaurant Name', 'Cleaned Address', 'City', 'Zip'], 
                        na_position='last').reset_index(drop=True)
    
    df = df.drop_duplicates(subset=['Restaurant Name', 'Cleaned Address'], keep='first')
    
    df = df.drop_duplicates(subset=['Restaurant Name', 'City'], keep='first')
    
    df = df.sort_values('City', na_position='last')
    df = df.drop_duplicates(subset=['Restaurant Name', 'Zip'], keep='first')
    
    df = df.dropna(subset=['City', 'Zip'], how='all')
    
    return df

def process_restaurant_data(input_file=RAW_RESTAURANTS_CSV, output_file=CLEANED_RESTAURANTS_CSV):
    """Main function to process restaurant data"""
    data = pd.read_csv(input_file)
    
    data[["Cleaned Address", "City", "State", "Zip"]] = data['Address'].apply(
        lambda x: pd.Series(clean_and_split_address(x))
    )
    
    data = data[data['Zip'].notna() & (data['Zip'] != '')]
    data = fill_missing_city(data)
    data = remove_duplicates(data)
    
    data.to_csv(output_file, index=False)
    print(f"Cleaned and deduplicated data has been saved to {output_file}")
    return data

if __name__ == "__main__":
    process_restaurant_data()
