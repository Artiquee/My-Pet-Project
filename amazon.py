import pandas
import numpy as np
from functions import tm_checker

def amz_items():
    excel_data_df = pandas.read_excel('./data/book.xlsx', sheet_name='Sheet0')
    # Amazon product links
    amz_links = excel_data_df['URL: Amazon'].tolist()
    # Amazon product title
    amz_titles = excel_data_df['Title'].tolist()
    # Amazon brand
    amz_brand = excel_data_df['Brand'].tolist()
    amz_brand = np.nan_to_num(amz_brand, nan=0)
    amz_brand = ['No brand' if x == 'nan' else x for x in amz_brand]
    # Amazon product category
    amz_categories = excel_data_df['Categories: Root'].tolist()
    # Amazon product price
    amz_buyboxes = excel_data_df['Buy Box: Current'].tolist()
    amz_buyboxes = np.nan_to_num(amz_buyboxes, nan=0)
    amz_no_buybox_price = excel_data_df['New: Current'].tolist()

    for x, y in enumerate(amz_buyboxes):
        if y == 0:
            amz_buyboxes[x] = amz_no_buybox_price[x]

    return [(x, str(amz_titles[i]), float(amz_buyboxes[i]), amz_brand[i], amz_brand[i], amz_categories[i]) for i, x in enumerate(amz_links)]

