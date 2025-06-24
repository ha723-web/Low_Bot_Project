
import os
import pandas as pd
from utils import normalize_reg_number, fuzzy_score

# === Load OCR-extracted image metadata ===
ocr_data = [
    {
        'Image': 'IN_DC_1_25-cv-00969_page2.webp',
        'Reg': 'VA1982408',
        'Title': 'Care Bears 2015 Core Style Guide',
        'Claimant': 'Those Characters From Cleveland, Inc.'
    },
    {
        'Image': 'IN_DC_1_25-cv-01049_page2.webp',
        'Reg': 'VA2308936',
        'Title': 'Staying Alive',
        'Claimant': ''
    },
    {
        'Image': 'IN_DC_1_25-cv-01050_page2.webp',
        'Reg': 'VA2403857',
        'Title': 'Daily Commute',
        'Claimant': 'Randall Ian Mackey'
    },
    {
        'Image': 'US_DIS_ILND_1_24cv7196_page3.webp',
        'Reg': 'VA2270346',
        'Title': 'Kaiju Frog',
        'Claimant': 'Ina Handayan Tomecek'
    }
]

ocr_df = pd.DataFrame(ocr_data)
ocr_df['Normalized_Reg'] = ocr_df['Reg'].apply(normalize_reg_number)

# === Load spreadsheet data ===
sheet_path = "data/records.csv"
df = pd.read_csv(sheet_path)
df['Normalized_Reg'] = df['Registration Number / Date'].apply(lambda x: normalize_reg_number(str(x).split('/')[0]))

# === Match each spreadsheet row to OCR image ===
matches = []

for idx, row in df.iterrows():
    best_score = 0
    best_match = None

    for _, image_row in ocr_df.iterrows():
        reg_score = fuzzy_score(row['Normalized_Reg'], image_row['Normalized_Reg'])
        title_score = fuzzy_score(row['Title'], image_row['Title'])
        claimant_score = fuzzy_score(str(row['Copyright Claimant']), str(image_row['Claimant']))
        total = (reg_score + title_score + claimant_score) / 3

        if total > best_score:
            best_score = total
            best_match = {
                'Sheet Title': row['Title'],
                'Image': image_row['Image'],
                'Matched Title': image_row['Title'],
                'Registration': row['Registration Number / Date'],
                'Claimant': image_row['Claimant'],
                'Score': round(total, 1)
            }

    if best_match and best_match['Score'] >= 50:
        matches.append(best_match)

# === Save results ===
out_df = pd.DataFrame(matches)
out_df.to_csv("output/spreadsheet_to_image_matches.csv", index=False)
print(f"✅ Matching complete. {len(matches)} spreadsheet rows linked to images.")
